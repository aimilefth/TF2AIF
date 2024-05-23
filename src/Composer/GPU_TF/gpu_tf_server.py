"""
Aimilios Leftheriotis
Microlab@NTUA

AI@EDGE project

This module defines the GpuTfServer class, which inherits from the BaseExperimentServer class defined in the experiment_server module. The GpuTfServer class represents a GPU-based implementation of the experiment server using native Tensorflow.

Methods:
- __init__(self, logger): Initializes the GpuTfServer instance, sets up the logger, initializes the kernel, and performs a warm-up run.

- init_kernel(self): This method is responsible for loading the TensorFlow model.

- warm_up(self): This method performs a warm-up run of the experiment by passing a dummy input through the TensorFlow model.

- experiment_single(self, input, run_total=1): Executes a single experiment, taking a numpy array as input and returning a numpy array as output.

- experiment_multiple(self, dataset, run_total): Executes multiple experiments, taking a tf.data.Dataset as input and returns a numpy array as output.

DO-NOT Edit this file
"""

import os
import time
import numpy as np
import tensorflow as tf

import experiment_server

class GpuTfServer(experiment_server.BaseExperimentServer):
    def __init__(self, logger):
        super().__init__(logger)
        # Initialize the Tensorflow model
        self.model = None
        # Initialize the kernel and perform warm-up
        self.init_kernel()
        self.warm_up()

    def init_kernel(self):
        """Initialize one time platform-specific server operations. Sets up the number of threads, loads the Tensorflow model, and configures execution providers."""
        print('init_kernel')
        start = time.perf_counter()
        # Load the Keras model from the specified path
        self.model = tf.keras.models.load_model(filepath=self.server_configs['MODEL_PATH'])
        # Store input name and shape in the server configurations        
        self.server_configs['input_shape'] = self.model.input_shape
        self.server_configs['output_shape'] = self.model.output_shape
        # Logging for debugging
        self.log("{}".format(self.server_configs['input_shape']))
        self.log("{}".format(self.server_configs['output_shape']))
        # Log the initialization time
        end = time.perf_counter()
        elapsed_time = end-start
        self.once_timings['init'] = elapsed_time
        self.log('Initialize time :\t {:.2f} ms'.format(elapsed_time*1000))
    
    def warm_up(self):
        """Run first time platform-specific server operations. Warm-up the Tensorflow model by running a dummy input."""
        print('warm_up')
        start = time.perf_counter()
        # Create a dummy input with zeros and set it as the input tensor
        x_dummy = np.zeros(shape=(self.server_configs['BATCH_SIZE'],) + self.server_configs['input_shape'][1:], dtype=np.float32)
        output_data = self.model.predict(x=x_dummy, batch_size=self.server_configs['BATCH_SIZE'], verbose=0)
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
        exp_output = self.model.predict(x=input, verbose=0)
        return exp_output

    def experiment_multiple(self, dataset, run_total):
        """
        Execute the experiment for multiple input data. Works only for on Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).
        Get a tf.data.Dataset as input, return a numpy array as output.
        """
        output_list = self.model.predict(x=dataset, verbose=0)
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