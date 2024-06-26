"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This module defines the CpuServer class, which inherits from the BaseExperimentServer class defined in the experiment_server module.
The CpuServer class represents a CPU-based implementation of the experiment server, optimized for running TensorFlow Lite models.

Overview:
- The CpuServer class is responsible for initializing the TensorFlow Lite environment, loading the model, and executing inference experiments.
- It includes methods for single and multiple inference runs, warm-up routines, and platform-specific preprocessing and postprocessing.

Classes:
- CpuServer: Inherits from BaseExperimentServer and implements CPU-specific initialization and inference methods.

Methods:
- __init__(self, logger): Initializes the CpuServer instance, sets up the logger, initializes the kernel, and performs a warm-up run.
- init_kernel(self): Sets up the TensorFlow Lite interpreter, resizes input tensor according to batch size, and allocates tensors.
- warm_up(self): Performs a warm-up run by passing a dummy input through the TensorFlow Lite interpreter.
- experiment_single(self, input, run_total=1): Executes a single experiment, taking a numpy array as input and returning a numpy array as output.
- experiment_multiple(self, dataset, run_total): Executes multiple experiments, taking a tf.data.Dataset as input and returning a numpy array as output.
- platform_preprocess(self, data): Placeholder for AI-framework/platform pair-specific preprocessing.
- platform_postprocess(self, data): Placeholder for AI-framework/platform pair-specific postprocessing.

DO NOT edit this file directly.
"""

import os
import time
import numpy as np
import tensorflow as tf
import experiment_server

class CpuServer(experiment_server.BaseExperimentServer):
    """
    CPU-specific server implementation for running TensorFlow Lite models.
    Inherits from BaseExperimentServer and implements CPU-specific initialization and inference methods.
    """
    def __init__(self, logger):
        """Initialize the CpuServer instance, set up the logger, initialize the kernel, and perform a warm-up run."""
        super().__init__(logger)
        self.interpreter = None
        self.server_configs['NUM_THREADS'] = int(os.environ['NUM_THREADS'])
        self.server_configs['input_details'] = None
        self.server_configs['output_details'] = None
        self.init_kernel()
        self.warm_up()

    def init_kernel(self):
        """
        Initialize one-time AI-framework/platform pair-specific server operations.
        Sets up the TensorFlow Lite interpreter, resizes input tensor, and allocates tensors.
        """
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

        # Store input and output details in server configurations
        self.server_configs['input_details'] = self.interpreter.get_input_details()
        self.server_configs['output_details'] = self.interpreter.get_output_details()

        # Log input and output details for debugging purposes
        self.log(f"Input Details: {self.server_configs['input_details'][0]['shape']}, {self.server_configs['input_details'][0]['dtype']}")
        self.log(f"Output Details: {self.server_configs['output_details'][0]['shape']}, {self.server_configs['output_details'][0]['dtype']}")

        end = time.perf_counter()
        self.once_timings['init'] = end - start
        self.log(f"Initialize time: {self.once_timings['init'] * 1000:.2f} ms")
    
    def warm_up(self):
        """
        Run first-time AI-framework/platform pair-specific server operations.
        Warm up the TensorFlow Lite interpreter by running a dummy input.
        """
        start = time.perf_counter()

        # Create a dummy input tensor filled with zeros
        x_dummy = np.zeros(shape=self.server_configs['input_details'][0]['shape'], dtype=np.float32)
        self.interpreter.set_tensor(self.server_configs['input_details'][0]['index'], x_dummy)

        # Run the dummy input through the TensorFlow Lite interpreter
        self.interpreter.invoke()
        _ = self.interpreter.get_tensor(self.server_configs['output_details'][0]['index'])

        end = time.perf_counter()
        self.once_timings['warm_up'] = end - start
        self.log(f"Warmup time: {self.once_timings['warm_up'] * 1000:.2f} ms")

    def experiment_single(self, input, run_total=1):
        """
        Execute the experiment for single input data.
        Works only in Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        Takes a numpy array as input and returns a numpy array as output.
        """
        # Set the provided input tensor and run the interpreter
        self.interpreter.set_tensor(self.server_configs['input_details'][0]['index'], input)
        self.interpreter.invoke()
        exp_output = self.interpreter.get_tensor(self.server_configs['output_details'][0]['index'])
        return exp_output

    def experiment_multiple(self, dataset, run_total):
        """
        Execute the experiment for multiple input data.
        Works only in Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).
        Takes a tf.data.Dataset as input and returns a numpy array as output.
        """
        output_list = []
        iterations = run_total // self.server_configs['BATCH_SIZE']
        remainder_iteration = 1 if iterations * self.server_configs['BATCH_SIZE'] != run_total else 0

        # Iterate through the dataset, batching data and feeding it to the model
        for i, element in enumerate(dataset.take(iterations + remainder_iteration)):
            x_test = element
            if i == iterations:  # Process any remainder data in the last iteration
                x_input = tf.zeros(shape=self.server_configs['input_details'][0]['shape'])
                x_input_list = tf.unstack(x_input)
                x_input_list[0:x_test.shape[0]] = x_test[:]
                x_input = tf.stack(x_input_list)
            else:
                x_input = x_test

            # Run the model and append results to output list
            self.interpreter.set_tensor(self.server_configs['input_details'][0]['index'], x_input)
            self.interpreter.invoke()
            output_data = self.interpreter.get_tensor(self.server_configs['output_details'][0]['index'])
            valid_outputs = x_test.shape[0] if i == iterations else self.server_configs['BATCH_SIZE']
            output_list.append(output_data[0:valid_outputs, :])

        # Concatenate all individual outputs to form a single numpy array
        concat_start = time.perf_counter()
        exp_output = np.concatenate(output_list, axis=0)
        concat_end = time.perf_counter()

        self.log(f"Concat output time: {(concat_end - concat_start) * 1000:.2f} ms")
        return exp_output

    def platform_preprocess(self, data):
        """Preprocess the input, specific to the platform requirement, not the experiment ones. Used in create_and_preprocess as the last step."""
        return data

    def platform_postprocess(self, data):
        """Postprocess the output, specific to the platform requirement, not the experiment ones. Used in postprocess as the first step."""
        return data
