"""
Aimilios Leftheriotis
Microlab@NTUA

AI@EDGE project

This module defines the AlveoServer class, which inherits from the BaseExperimentServer class defined in the experiment_server module. The AlveoServer class represents an Alveo-based implementation of the experiment server, optimized for running Vitis AI models.

Methods:
- __init__(self, logger): Initializes the AlveoServer instance, sets up the logger, decides the number of threads based on the batch size and the native batch sizes of the selected device, initializes the kernel, and performs a warm-up run.

- init_kernel(self): This method is responsible for setting up the Vitis AI Runner, loading the model, creating the DPU runners and determining input and output dimensions and scales.

- warm_up(self): This method performs a warm-up run of the experiment.

- decide_num_threads(self): This method decides the number of threads based on the batch size and the native batch sizes of the selected device.

- experiment_single(self, input, run_total=1): This method is designed to run a single experiment (i.e., a single run of the DPU runners) and collect the result.

- experiment_multiple(self, dataset, run_total): This method is designed to run multiple experiments (i.e., multiple runs of the DPU runners) and collect the results. It's capable of running experiments in parallel using multiple threads.

- platform_preprocess(self, data): This methods is responsible for pre-processing the data for this specific platform.

- platform_postprocess(self, data) : These methods are responsible for pre-processing the data for this specific platform.

- runDPU_multiple(self, id, start_output, dpu_runner, dataset, num_of_data, output_list): This method is used by experiment_multiple to execute the DPU runner for a certain portion of the dataset in a separate thread.

DO-NOT Edit this file
"""

import os
import time
import numpy as np
import tensorflow as tf
import vart
import xir
import threading
from typing import List

import experiment_server
# Custom module
import utils

class AlveoServer(experiment_server.BaseExperimentServer):
    def __init__(self, logger):
        super().__init__(logger)
        # Initialize the list that holds the VitisAI dpu runners
        self.all_dpu_runners = []
        # ALVEO-specific configuration setup
        self.server_configs['input_scale'] = None
        self.server_configs['output_scale'] = None
        self.server_configs['input_ndim'] = None
        self.server_configs['output_ndim'] = None
        self.server_configs['DEVICE'] = os.environ['DEVICE']
        self.server_configs['CHANNELS_FIRST'] = utils.strtobool(os.environ['CHANNELS_FIRST'])
        self.server_configs['native_batch_sizes'] = {
            'U280_L': 1,
            'U280_H': 3
        }
        # Determine the number of threads needed based on the device's native batch size and current batch size
        self.server_configs['threads'] = self.decide_num_threads()
        # Initialize the kernel and perform warm-up
        self.init_kernel()
        self.warm_up()

    def init_kernel(self):
        """Initialize one time platform-specific server operations. Sets up the dpu runners, loads the model, and configures execution providers."""
        def get_child_subgraph_dpu(graph: "Graph") -> List["Subgraph"]:
            # Internal helper function to get child subgraphs for DPU from a graph
            assert graph is not None, "'graph' should not be None."
            root_subgraph = graph.get_root_subgraph()
            assert (root_subgraph is not None), "Failed to get root subgraph of input Graph object."
            if root_subgraph.is_leaf:
                return []
            child_subgraphs = root_subgraph.toposort_child_subgraph()
            assert child_subgraphs is not None and len(child_subgraphs) > 0
            return [
                cs
                for cs in child_subgraphs
                if cs.has_attr("device") and cs.get_attr("device").upper() == "DPU"
            ]
        
        print('init_kernel')
        start = time.perf_counter()
        # Load Model
        g = xir.Graph.deserialize(self.server_configs['MODEL_PATH'])
        subgraphs = get_child_subgraph_dpu(g)
        # Create DPU runners for each thread
        for i in range(self.server_configs['threads']):
            try:
                self.all_dpu_runners.append(vart.Runner.create_runner(subgraphs[0], "run"))
            except Exception as e:
                print(e)
                self.log({}.format(e))
        # Store input and output settings in the server configurations        
        input_fixpos = self.all_dpu_runners[0].get_input_tensors()[0].get_attr("fix_point")
        self.server_configs['input_scale'] = 2**input_fixpos
        output_fixpos = self.all_dpu_runners[0].get_output_tensors()[0].get_attr("fix_point")
        self.server_configs['output_scale'] = 1 / (2**output_fixpos)
        self.server_configs['input_ndim'] = tuple(self.all_dpu_runners[0].get_input_tensors()[0].dims)
        self.server_configs['output_ndim'] = tuple(self.all_dpu_runners[0].get_output_tensors()[0].dims)
        # Logging for debugging
        self.log("{}".format(self.server_configs['input_scale']))
        self.log("{}".format(self.server_configs['output_scale']))
        self.log("{}".format(self.server_configs['input_ndim']))
        self.log("{}".format(self.server_configs['output_ndim']))
        # Log the initialization time
        end = time.perf_counter()
        elapsed_time = end-start
        self.once_timings['init'] = elapsed_time
        self.log('Initialize time :\t {:.2f} ms'.format(elapsed_time*1000))
    
    def warm_up(self):
        """Run first time platform-specific server operations. Warm-up the dpus by running a dummy input."""
        def warm_up_dpu(dpu_runner, input_ndim, output_ndim):
            # Internal function to run a warm-up iteration for the DPU
            inputData = [np.empty(input_ndim, dtype=np.int8, order="C")]
            outputData = [np.empty(output_ndim, dtype=np.int8, order="C")]
            job_id = dpu_runner.execute_async(inputData,outputData)
            dpu_runner.wait(job_id)
            return
        
        print('warm_up')
        start = time.perf_counter()
        thread_list = []
        for dpu_runner in self.all_dpu_runners:
            thread_list.append(threading.Thread(target=warm_up_dpu, args=(dpu_runner, self.server_configs['input_ndim'], self.server_configs['output_ndim'])))
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        # Log the warm-up time
        end = time.perf_counter()
        elapsed_time = end-start
        self.once_timings['warm_up'] = elapsed_time
        self.log('Warmup time :\t {:.2f} ms'.format(elapsed_time*1000))
    
    def decide_num_threads(self):
        """Decide the number of threads based on batch size and device's native batch sizes."""
        if(self.server_configs['BATCH_SIZE'] % self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']]> 0):
            return self.server_configs['BATCH_SIZE'] // self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']] + 1
        else:
            return self.server_configs['BATCH_SIZE'] // self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']]

    def experiment_single(self, input, run_total=1):
        """
        Execute the experiment for single input data. Works only for on Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        Get a numpy.array as input, return a numpy.array as output.
        """
        outputData = []
        outputData.append([np.empty(self.server_configs['output_ndim'], dtype=np.int8, order="C")])
        inputData = [np.empty(self.server_configs['input_ndim'], dtype=np.int8, order="C")]
        imageRun = inputData[0]
        imageRun[0:input.shape[0]] = input
        job_id = self.all_dpu_runners[0].execute_async(inputData,outputData[0])
        self.all_dpu_runners[0].wait(job_id)
        exp_output = outputData[0][0][0]
        return exp_output

    def experiment_multiple(self, dataset, run_total):
        """
        Execute the experiment for multiple input data. Works only for on Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).
        Get a tf.data.Dataset as input, return a numpy array as output.
        """
        # Create the thread_list_arguments to runDPU_multiple
        thread_list_arguments = []
        start=0
        # Correct the batch size
        dataset = dataset.unbatch().batch(self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']])
        iterations = run_total // self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']]
        # Prepare arguments for threading, split the dataset across multiple threads
        for i in range(self.server_configs['threads']):
            if(i == self.server_configs['threads'] - 1): # Process any remainder data in the last thread
                num_of_data = run_total - start*self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']]
                ds_val_split = dataset.skip(start)
            else:
                end = start + (iterations // self.server_configs['threads'])
                num_of_data = (end-start) * self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']]
                ds_val_split = dataset.skip(start).take(end-start)
            thread_list_arguments.append((  i,
                                            start*self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']],
                                            self.all_dpu_runners[i],
                                            ds_val_split,
                                            num_of_data))
            start=end
        output_list = [None] * run_total
        thread_list = []
        for thread_tuple in thread_list_arguments:
            # Each thread will execute the `runDPU_multiple` method
            thread_list.append(threading.Thread(target=self.runDPU_multiple, args=thread_tuple + (output_list,)))
        # Start and join threads to ensure all threads complete execution
        for thread in thread_list:
            thread.start()
        for thread in thread_list:
            thread.join()
        # Concatenate all individual outputs to form a single numpy array
        concat_start = time.perf_counter()
        exp_output = np.concatenate(output_list, axis=0)
        concat_end = time.perf_counter()
        # Log the time taken to concatenate outputs
        self.log("Concat output time {:.2f} ms".format((concat_end-concat_start)*1000))
        return exp_output

    def platform_preprocess(self, data):
        """Preprocess the input, but specific to the platform requirement, not the experiment ones. Used on create_and_preprocess as last step."""
        data = data * self.server_configs['input_scale']
        data = tf.cast(data, tf.int8)
        if(self.server_configs['CHANNELS_FIRST'] == True):
            """Convert a tensor from NCHW to NHWC format. Vitis AI needs NHWC even if input model is NCHW"""
            data = tf.transpose(data, [0, 2, 3, 1])
        return data

    def platform_postprocess(self, data):
        """Preprocess the input, but specific to the platform requirement, not the experiment ones. Used on create_and_preprocess as last step."""
        data = data.astype(np.float32)
        data = data * self.server_configs['output_scale']
        return data

    def runDPU_multiple(self, id, start_output, dpu_runner, dataset, num_of_data, output_list):
        """
        Thread for running the dpu_runner on experiment_multiple, ALVEO-specific.
        Could be moved to AlveoServer but generality would have cost in perfomance.
        Get a tf.data.Dataset as input, adds the outputs to the output_list (List of numpy arrays)
        """
        # Log thread-specific details for debugging
        self.log('id: {}, start: {}, batch: {}, num_of_data: {}'.format(id, start_output, self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']], num_of_data))
        outputData = []
        iterations = num_of_data // self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']]
        if(iterations * self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']] != num_of_data):
            remainder_iteration = 1
        else:
            remainder_iteration = 0
        for i in range(iterations + remainder_iteration):
            outputData.append([np.empty(self.server_configs['output_ndim'], dtype=np.int8, order="C")])
        # Iterate through the dataset, batching data and feeding to the model
        for i, element in enumerate(dataset.take(iterations + remainder_iteration)):
            x_test = element.numpy()
            if(i == iterations): # Process any remainder data in the last iteration
                inputData = [np.empty(self.server_configs['input_ndim'], dtype=np.int8, order="C")]
                imageRun = inputData[0]
                imageRun[0:x_test.shape[0]] = x_test
            else:
                inputData = [x_test]
            # Run the model and append results to output list
            job_id = dpu_runner.execute_async(inputData,outputData[i])
            dpu_runner.wait(job_id)
            for j in range(x_test.shape[0]):
                output_list[start_output + i*self.server_configs['native_batch_sizes'][self.server_configs['DEVICE']] + j] = outputData[i][0][j]
        return
