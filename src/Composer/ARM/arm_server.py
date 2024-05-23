"""
Aimilios Leftheriotis
Microlab@NTUA

AI@EDGE project

This module defines the ArmServer class, which inherits from the BaseExperimentServer class defined in the experiment_server module. The ArmServer class represents an ARM-based implementation of the experiment server, optimized for running TensorFlow Lite models.

Methods:
- __init__(self, logger): Initializes the ArmServer instance, sets up the logger, decides the number of threads for the interpreter, initializes the kernel, and performs a warm-up run.

- init_kernel(self): This method is responsible for setting up the TensorFlow Lite interpreter, resizing input tensor according to batch size, and allocating tensors.

- warm_up(self): This method performs a warm-up run of the experiment by passing a dummy input through the TensorFlow Lite interpreter.

- decide_num_threads(self): This method decides the number of threads based on the available ARM cores.

- experiment_single(self, input, run_total=1): Executes a single experiment, taking a numpy array as input and returning a numpy array as output.

- experiment_multiple(self, dataset, run_total): Executes multiple experiments, taking a tf.data.Dataset as input and returns a numpy array as output.

- platform_preprocess(self, data): Executes preprocessing steps on the data at the platform level, (Tensorflow Lite specific details). Handles data type conversions if needed.

- platform_postprocess(self, data): Executes postprocessing steps on the data at the platform level, (Tensorflow Lite specific details). Handles data type conversions if needed.

DO-NOT Edit this file
"""


import os
import time
import numpy as np
import tensorflow as tf

import experiment_server

class ArmServer(experiment_server.BaseExperimentServer):
    def __init__(self, logger):
        super().__init__(logger)
        # Initialize the TensorFlow Lite interpreter attribute
        self.intepreter = None
        # ARM-specific server configurations
        self.server_configs['NUM_THREADS'] = int(os.environ['NUM_THREADS'])
        self.server_configs['input_details'] = None
        self.server_configs['output_details'] = None
        # Initialize the kernel and perform warm-up
        self.init_kernel()
        self.warm_up()

    def init_kernel(self):
        """Initialize one time platform-specific server operations. Setup TensorFlow Lite interpreter, tensors, and related configurations."""
        print('init_kernel')
        start = time.perf_counter()
        # Load the TensorFlow Lite model with specified number of threads
        self.interpreter = tf.lite.Interpreter(model_path=self.server_configs['MODEL_PATH'], num_threads=self.server_configs['NUM_THREADS'])
        # Resize the input tensor to match the specified batch size
        input_details = self.interpreter.get_input_details()
        shape = input_details[0]['shape']
        shape[0] = self.server_configs['BATCH_SIZE']
        self.interpreter.resize_tensor_input(input_details[0]['index'], shape)
        # Allocate memory for tensors in the interpreter
        self.interpreter.allocate_tensors()
        # Store input and output details in the server configurations
        self.server_configs['input_details'] = self.interpreter.get_input_details()
        self.server_configs['output_details'] = self.interpreter.get_output_details()
        # Log input and output details for debugging purposes
        self.log("{}".format(self.server_configs['input_details'][0]['shape']))
        self.log("{}".format(self.server_configs['input_details'][0]['dtype']))
        self.log("{}".format(self.server_configs['output_details'][0]['shape']))
        self.log("{}".format(self.server_configs['output_details'][0]['dtype']))
        # Log the initialization time
        end = time.perf_counter()
        elapsed_time = end-start
        self.once_timings['init'] = elapsed_time
        self.log('Initialize time :\t {:.2f} ms'.format(elapsed_time*1000))
    
    def warm_up(self):
        """Run first time platform-specific server operations. Warm-up the TensorFlow Lite interpreter by running a dummy input."""
        print('warm_up')
        start = time.perf_counter()
        # Create a dummy input with zeros and set it as the input tensor
        x_dummy = np.zeros(shape=self.server_configs['input_details'][0]['shape'], dtype=np.uint8)
        self.interpreter.set_tensor(self.server_configs['input_details'][0]['index'], x_dummy)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.server_configs['output_details'][0]['index'])
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
        # Set the provided input tensor and run the interpreter
        self.interpreter.set_tensor(self.server_configs['input_details'][0]['index'], input)
        self.interpreter.invoke()
        exp_output = self.interpreter.get_tensor(self.server_configs['output_details'][0]['index'])
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
                x_input = tf.zeros(shape =self.server_configs['input_details'][0]['shape'])
                x_input_list = tf.unstack(x_input)
                x_input_list[0:x_test.shape[0]] = x_test[:]
                x_input = tf.stack(x_input_list)
            else:
                x_input = x_test
            # Run the model and append results to output list
            self.interpreter.set_tensor(self.server_configs['input_details'][0]['index'], x_input)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.server_configs['output_details'][0]['index'])
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
        # Convert data if dtype is uint8
        if(self.server_configs['input_details'][0]['dtype'] == np.uint8):
            input_scale, input_zero_point = self.server_configs['input_details'][0]["quantization"]
            data = data / input_scale + input_zero_point
            data = tf.cast(x=data, dtype=tf.uint8)
        return data

    def platform_postprocess(self, data):
        """Postprocess the output, but specific to the platform requirement, not the experiment ones.  Used on postprocess as first step."""
        # Convert data if dtype is uint8
        if(self.server_configs['output_details'][0]['dtype'] == np.uint8):
            output_scale, output_zero_point = self.server_configs['output_details'][0]["quantization"]
            data = data.astype(np.float32)
            data = (data - output_zero_point)*output_scale
        return data