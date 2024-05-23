"""
Aimilios Leftheriotis
Microlab@NTUA

AI@EDGE project

This module defines the AgxServer class, which inherits from the BaseExperimentServer class defined in the experiment_server module. The AgxServer class represents an AGX-based implementation of the experiment server, optimized for running ONNX Runtime models.

Methods:
- __init__(self, logger): Initializes the AgxServer instance, sets up the logger, initializes the kernel, and performs a warm-up run.

- init_kernel(self): This method is responsible for setting up the ONNX Runtime interpreter, configuring the execution providers for TensorRT and CUDA, and loading the model.

- warm_up(self): This method performs a warm-up run of the experiment by passing a dummy input through the ONNX Runtime session.

- experiment_single(self, input, run_total=1): Executes a single experiment, taking a numpy array as input and returning a numpy array as output.

- experiment_multiple(self, dataset, run_total): Executes multiple experiments, taking a tf.data.Dataset as input and returns a numpy array as output.

DO-NOT Edit this file
"""


import os
import time
import numpy as np
import tensorflow as tf
import onnxruntime as ort

import experiment_server

class AgxServer(experiment_server.BaseExperimentServer):
    def __init__(self, logger):
        super().__init__(logger)
        # Initialize the ONNX Runtime inference session
        self.sess = None
        # AGX-specific configuration setup (ONNX)
        self.server_configs['CALIBRATION'] = os.environ['CALIBRATION']
        self.server_configs['providers'] = None
        self.server_configs['input_name'] = None
        # Initialize the kernel and perform warm-up
        self.init_kernel()
        self.warm_up()
    
    def init_kernel(self):
        """Initialize one time platform-specific server operations. Sets up the ONNX Runtime inference session, loads the model, and configures execution providers."""
        print('init_kernel')
        start = time.perf_counter()
        # Define providers and their configurations
        self.server_configs['providers'] = [
            ('TensorrtExecutionProvider',{
             'device_id' : 0,
             'trt_fp16_enable' : False,
             'trt_int8_enable' : True,
             'trt_int8_calibration_table_name' : self.server_configs['CALIBRATION'],
             'trt_engine_cache_enable' : False
             }),
            ('CUDAExecutionProvider', {
             'device_id' : 0,
             })
        ] 
        # Session options for ONNX Runtime
        sess_opt = ort.SessionOptions()
        sess_opt.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
        # Creating an inference session        
        self.sess = ort.InferenceSession(path_or_bytes=self.server_configs['MODEL_PATH'], sess_options=sess_opt, providers=self.server_configs['providers'])
        # Store input name and shape in the server configurations        
        self.server_configs['input_name'] = self.sess.get_inputs()[0].name
        self.server_configs['input_shape'] = self.sess.get_inputs()[0].shape
        # Logging for debugging
        self.log("{}".format(self.sess.get_providers()))
        self.log("{}".format(self.sess.get_provider_options()))
        self.log("{}".format(self.sess.get_session_options()))
        self.log("{}".format(self.server_configs['input_name']))
        self.log("{}".format(self.server_configs['input_shape']))
        # Log the initialization time
        end = time.perf_counter()
        elapsed_time = end-start
        self.once_timings['init'] = elapsed_time
        self.log('Initialize time :\t {:.2f} ms'.format(elapsed_time*1000))
    
    def warm_up(self):
        """Run first time platform-specific server operations. Warm-up the ONNX Runtime inference session by running a dummy input."""
        print('warm_up')
        start = time.perf_counter()
        # Create a dummy input with zeros and set it as the input tensor
        x_dummy = tf.zeros(shape=self.server_configs['input_shape'], dtype=tf.float32).numpy()
        output_data = self.sess.run([],{self.server_configs['input_name']: x_dummy})[0]
        # Log the warm-up time
        end = time.perf_counter()
        elapsed_time = end-start
        self.once_timings['warm_up'] = elapsed_time
        self.log('Warmup time :\t {:.2f} ms'.format(elapsed_time*1000))

    def experiment_single(self, input, run_total=1):
        """
        Execute the experiment for single input data. Works only for on Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        Get a numpy.array as input, return a numpy.array as output.
        """
        exp_output = self.sess.run([],{self.server_configs['input_name']: input})[0]
        return exp_output

    def experiment_multiple(self, dataset, run_total):
        """
        Execute the experiment for multiple input data. Works only for on Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).
        Get a tf.data.Dataset as input, return a numpy array as output.
        """
        output_list = []
        iterations = run_total // self.server_configs['BATCH_SIZE']
        if(iterations * self.server_configs['BATCH_SIZE'] != run_total):
            remainder_iteration = 1
        else:
            remainder_iteration = 0
        # Iterate through the dataset, batching data and feeding to the model
        for i, element in enumerate(dataset.take(iterations + remainder_iteration)):
            x_test = element
            if(i == iterations): # Process any remainder data in the last iteration
                x_input = tf.zeros(shape = self.server_configs['input_shape'])
                x_input_list = tf.unstack(x_input)
                x_input_list[0:x_test.shape[0]] = x_test[:]
                x_input = tf.stack(x_input_list).numpy()
            else:
                x_input = x_test.numpy()
            # Run the model and append results to output list
            output_data = self.sess.run([],{self.server_configs['input_name']: x_input})[0]
            if(i == iterations): # Consider valid outputs for the last iteration
                valid_outputs = x_test.shape[0]
            else:
                valid_outputs = self.server_configs['BATCH_SIZE']
            output_list.append(output_data[0:valid_outputs,:])
        # Concatenate all individual outputs to form a single numpy array
        concat_start = time.perf_counter()
        exp_output = np.concatenate(output_list, axis=0)
        concat_end = time.perf_counter()
        # Log the time taken to concatenate outputs
        self.log("Concat output time {:.2f} ms".format((concat_end-concat_start)*1000))
        return exp_output

    def platform_preprocess(self, data):
        """Preprocess the input, but specific to the platform requirement, not the experiment ones. Used on create_and_preprocess as last step."""
        return data

    def platform_postprocess(self, data):
        """Postprocess the output, but specific to the platform requirement, not the experiment ones.  Used on postprocess as first step."""
        return data