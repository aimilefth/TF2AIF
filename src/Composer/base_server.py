"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This module defines the BaseServer class, which provides the foundational functionality for server operations 
across various AI-framework/platform combinations and experiments.

Overview:
- The BaseServer class is designed to be extended by AI-framework/platform pair-specific server classes 
  (e.g., AgxServer, AlveoServer, ArmServer, CpuServer, GpuServer) to customize behavior and processing as 
  needed for each platform.
- This class encapsulates common server functionalities, including:
  - Initialization of server configurations, metrics, timings, and AI characteristics.
  - Logging and Redis connection management.
  - Inference workflow management from decoding input to encoding output.
  - Benchmark metrics calculation and logging.
  - Redis data creation and sending.
  - Saving and logging metrics for analysis.

Functionality:
- Initialization:
  - Loads server configurations, metrics, and AI characteristics.
  - Sets up logging and Redis connections if required.
- Inference Workflow:
  - Manages the end-to-end inference process, including input decoding, data preprocessing, 
    experiment execution, postprocessing, and output encoding.
  - Each step in the workflow is designed to be overridden by subclass implementations to provide 
    AI-framework/platform pair-specific or experiment-specific functionality.
- Metrics and Logging:
  - Calculates various benchmarks related to inference latency and throughput.
  - Saves and logs metrics for performance analysis.
  - Optionally sends metrics to a Redis server for real-time monitoring.

Note:
- This module also imports and uses a custom module named 'utils' for various utility functions.
- The methods decode_input, create_and_preprocess, experiment_single, experiment_multiple, postprocess, 
  and encode_output are placeholders here and should be overridden by the subclasses to provide 
  AI-framework/platform pair-specific and/or experiment-specific functionality.

DO NOT edit this file directly.
"""

import os
import time
from dotenv import load_dotenv
import numpy as np
import utils  # Custom module for utility functions

class BaseServer:
    """
    This is the foundational class for server operations across different platforms and experiments.
    It provides methods for managing the server's workflow, from data input to response generation, 
    and also for metrics, logging, and Redis connections.
    """
    def __init__(self, my_logger):
        """Initialize server configurations, metrics, timings, and AI characteristics."""
        self.logger = my_logger
        self.my_redis = None
        self.my_metrics_list = utils.LimitedList(int(os.environ['METRICS_LIST_SIZE']))

        # Configuration settings for the server
        self.server_configs = {
            'MODEL_PATH': os.environ['MODEL_NAME'],
            'BATCH_SIZE': int(os.environ['BATCH_SIZE']),
            'SEND_METRICS': utils.strtobool(os.environ['SEND_METRICS']),
            'AIF_timestamp': int(time.perf_counter()*1000),
            'SERVER_MODE': utils.decode_server_mode(os.environ['SERVER_MODE'])  # 0 == LAT, 1 == THR
        }

        # Timings related to server operations
        self.once_timings = {
            'init': None,
            'warm_up': None
        }
        self.inference_timings = {
            'decode_input': None,
            'create_and_preprocess': None,
            'reshape_input': None,
            'experiment': None,
            'reshape_output': None,
            'postprocess': None,
            'encode_output': None,
            'full_inference': None,
            'redis_send': None,
            'save_metrics': None
        }

        # Metrics related to server operations
        self.inference_metrics = {
            'processing_latency': None,
            'data_preparation': None,
            'execution_latency': None,
            'throughput': None,
            'dataset_size': None,
            'batch_size': self.server_configs['BATCH_SIZE']
        }

        # Characteristics of the AI Framework
        self.aif_characteristics = {
            'app_name': os.environ['APP_NAME'],
            'network_name': os.environ['NETWORK_NAME'],
            'network_type': os.environ['NETWORK_TYPE'],
            'device': os.environ['AI_DEVICE'],
            'focus': os.environ['FOCUS']
        }

        self.create_redis()  # Create a Redis connection if required
        self.load_env_variables()

    def log(self, string_message):
        """Log a message using the server's logger."""
        self.logger.info(string_message)
    
    def load_env_variables(self):
        """Load environment variables from a specified .env file on ENV_FILE env variable."""
        load_dotenv(dotenv_path=os.environ['ENV_FILE'])

    def set_experiment_configs(self):
        """Define experiment configurations. Must be overridden by experiment_server.py (BaseExperimentServer)."""
        raise AssertionError('Forgot to overload set_experiment_configs. Must be overridden by experiment_server.py (BaseExperimentServer).')

    def create_redis(self):
        """Attempt to create a Redis connection."""
        if self.server_configs['SEND_METRICS']:
            try:
                utils.read_node_env_variables()
                self.my_redis = utils.create_redis()
                self.log('Created Redis connection')
            except Exception as e:
                self.log(f"Could not create Redis connection: {str(e)}")

    def init_kernel(self):
        """
        Initialize one-time AI-framework/platform pair-specific server operations. Must be overridden by {pair}_server.py ({Pair}Server).
        The function should calculate the elapsed time, saving it at self.once_timings['init'], and log it accordingly.
        """
        raise AssertionError('Forgot to overload init_kernel. Must be overridden by {pair}_server.py ({Pair}Server).')

    def warm_up(self):
        """
        Run first-time platform-specific server operations. Must be overridden by {pair}_server.py ({Pair}Server).
        The function should calculate the elapsed time, saving it at self.once_timings['warm_up'], and log it accordingly.
        """
        raise AssertionError('Forgot to overload warm_up. Must be overridden by {pair}_server.py ({Pair}Server).')

    def send_response(self, encoded_output):
        """Send a response after processing. Must be overridden by experiment_server.py (BaseExperimentServer)."""
        raise AssertionError('Forgot to overload send_response. Must be overridden by experiment_server.py (BaseExperimentServer).')

    def inference(self, indata):
        """
        Handle the entire inference process, including:
        - Decoding input
        - Data preprocessing
        - Experiment execution
        - Data postprocessing
        - Encoding output
        """

        # Starting timer for the full inference process
        full_start = time.perf_counter()
        
        # Executing the input decoding process
        decode_input_start = time.perf_counter()
        decoded_input, run_total = self.decode_input(indata=indata)
        assert not (self.server_configs['SERVER_MODE'] == 0 and run_total > 1), \
            f"AssertionError: server_mode is 0 and run_total is > 1, got server_mode: {self.server_configs['SERVER_MODE']} and run_total: {run_total}"
        self.log(f"Dataset size: {run_total}")
        decode_input_end = time.perf_counter()
        self.inference_timings['decode_input'] = decode_input_end - decode_input_start
        self.log(f"Decode Input time: {self.inference_timings['decode_input'] * 1000:.2f} ms")

        # Executing the dataset creation and preprocessing
        create_and_preprocess_start = time.perf_counter()
        dataset = self.create_and_preprocess(decoded_input=decoded_input, run_total=run_total)
        create_and_preprocess_end = time.perf_counter()
        self.inference_timings['create_and_preprocess'] = create_and_preprocess_end - create_and_preprocess_start
        self.log(f"Create and Preprocess time: {self.inference_timings['create_and_preprocess'] * 1000:.2f} ms")
        
        # Reshaping input data if in Latency Server Mode (self.server_configs['SERVER_MODE'] == 0)
        reshape_input_start = time.perf_counter()
        if self.server_configs['SERVER_MODE'] == 0:
            dataset = self.reshape_input(input=dataset)
        reshape_input_end = time.perf_counter()
        self.inference_timings['reshape_input'] = reshape_input_end - reshape_input_start
        self.log(f"Reshape input time: {self.inference_timings['reshape_input'] * 1000:.2f} ms")

        # Running the experiment based on the server mode
        experiment_start = time.perf_counter()
        if self.server_configs['SERVER_MODE'] == 0:
            assert self.server_configs['BATCH_SIZE'] == 1, \
                f"Batch size should be equal to 1 in cases where server_mode == 0, got {self.server_configs['BATCH_SIZE']}"
            exp_output = self.experiment_single(input=dataset, run_total=run_total)
        elif self.server_configs['SERVER_MODE'] == 1:
            exp_output = self.experiment_multiple(dataset=dataset, run_total=run_total)
        else:
            raise AssertionError(f"Server Mode is neither 0 nor 1 (LAT or THR), got {self.server_configs['SERVER_MODE']}")
        experiment_end = time.perf_counter()
        self.inference_timings['experiment'] = experiment_end - experiment_start
        self.log(f"Experiment time: {self.inference_timings['experiment'] * 1000:.2f} ms")

        # Reshaping the experiment output
        reshape_output_start = time.perf_counter()
        exp_output = self.reshape_output(exp_output=exp_output, run_total=run_total)
        reshape_output_end = time.perf_counter()
        self.inference_timings['reshape_output'] = reshape_output_end - reshape_output_start
        self.log(f"Reshape output time: {self.inference_timings['reshape_output'] * 1000:.2f} ms")

        # Post-processing the experiment output
        postprocess_start = time.perf_counter()
        output = self.postprocess(exp_output=exp_output, run_total=run_total)
        postprocess_end = time.perf_counter()
        self.inference_timings['postprocess'] = postprocess_end - postprocess_start
        self.log(f"Postprocess time: {self.inference_timings['postprocess'] * 1000:.2f} ms")

        # Encoding the final output
        encode_output_start = time.perf_counter()
        encoded_output = self.encode_output(output=output)
        encode_output_end = time.perf_counter()
        self.inference_timings['encode_output'] = encode_output_end - encode_output_start
        self.log(f"Encode Output time: {self.inference_timings['encode_output'] * 1000:.2f} ms")

        # Calculating and storing the full elapsed time for the inference
        full_end = time.perf_counter()
        self.inference_timings['full_inference'] = full_end - full_start

        # Various post-inference operations
        self.benchmarks(run_total=run_total)
        self.redis_create_send()
        self.save_metrics()
        self.prints()
        return encoded_output

    def decode_input(self, indata):
        """
        Decode input data. Must be overridden by experiment_server.py (BaseExperimentServer).
        indata is the input from the request. 
        Output needs to be: return decoded_input, run_total
        - decoded_input: the data (in any format).
        - run_total: the number of data items.
        decoded_input becomes the input for create_and_preprocess, which is also defined in experiment_server.py.
        """
        raise AssertionError('Forgot to overload decode_input. Must be overridden by experiment_server.py (BaseExperimentServer).')

    def create_and_preprocess(self, decoded_input, run_total):
        """
        Create and preprocess the dataset. Must be overridden by experiment_server.py (BaseExperimentServer).
        Gets decoded_input from decode_input() and outputs dataset.
        dataset NEEDS to be:
        a) a numpy.array in Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        b) a tf.data.Dataset in Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).
        """
        raise AssertionError('Forgot to overload create_and_preprocess. Must be overridden by experiment_server.py (BaseExperimentServer).')

    def reshape_input(self, input):
        """
        Reshape input data if necessary, works only in Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        Takes a numpy array as input and returns a reshaped numpy array as output.
        It reshapes the input based on the `expected_input` field in the self.experiment_configs in the set_experiment_configs method of experiment_server.py.
        self.experiment_configs['expected_input'] must be batched input, e.g., (None, 224, 224, 3).
        """
        if 'expected_input' in self.experiment_configs:
            batched_expected_input = (self.server_configs['BATCH_SIZE'],) + self.experiment_configs['expected_input'][1:]
            input = np.reshape(input, batched_expected_input)
        return input

    def experiment_single(self, input, run_total=1):
        """
        Execute the experiment for single input data. Works only in Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        Must be overridden by {pair}_server.py ({Pair}Server).
        Takes a numpy.array as input and returns a numpy.array as output.
        """
        raise AssertionError('Forgot to overload experiment_single. Must be overridden by {pair}_server.py ({Pair}Server).')

    def experiment_multiple(self, dataset, run_total):
        """
        Execute the experiment for multiple input data. Works only in Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).
        Must be overridden by {pair}_server.py ({Pair}Server).
        Takes a tf.data.Dataset as input and returns a numpy array as output.
        """
        raise AssertionError('Forgot to overload experiment_multiple. Must be overridden by {pair}_server.py ({Pair}Server).')

    def reshape_output(self, exp_output, run_total):
        """
        Reshape experiment output if necessary.
        Takes a numpy array as input and returns a reshaped numpy array as output.
        It reshapes the output based on the `expected_output` field in the self.experiment_configs in the set_experiment_configs method of experiment_server.py.
        self.experiment_configs['expected_output'] must be batched output, e.g., (None, 1000).
        """
        if 'expected_output' in self.experiment_configs:
            batched_expected_output = (run_total,) + self.experiment_configs['expected_output'][1:]
            exp_output = np.reshape(exp_output, batched_expected_output)
        return exp_output
    
    def postprocess(self, exp_output, run_total):
        """
        Post-process the experiment output. Must be overridden by experiment_server.py (BaseExperimentServer).
        Input is a numpy array.
        output becomes the input for encode_output (in any format that fits).
        """
        raise AssertionError('Forgot to overload postprocess. Must be overridden by experiment_server.py (BaseExperimentServer).')

    def encode_output(self, output):
        """
        Encode the processed output.
        Takes the input from postprocess and passes the encoded_output to the send_response function.
        """
        raise AssertionError('Forgot to overload encode_output. Must be overridden by experiment_server.py (BaseExperimentServer).')
    
    def benchmarks(self, run_total):
        """Calculate various benchmarks based on inference metrics."""
        assert isinstance(self.inference_timings['experiment'], float), \
            f"This variable is not float, it is {type(self.inference_timings['experiment']).__name__} with value {self.inference_timings['experiment']}"
        timetotal_execution = self.inference_timings['experiment']
        avg_time_execution = timetotal_execution / run_total
        full_time = self.inference_timings['full_inference']
        avg_full_time = full_time / run_total
        self.inference_metrics['data_preparation_latency'] = (avg_full_time - avg_time_execution) * 1000
        self.inference_metrics['execution_latency'] = avg_time_execution * 1000
        self.inference_metrics['processing_latency'] = avg_full_time * 1000
        self.inference_metrics['throughput'] = run_total / full_time
        self.inference_metrics['dataset_size'] = run_total

    def redis_create_send(self):
        """Create metric data and send it to Redis."""
        if self.server_configs['SEND_METRICS']:
            create_start = time.perf_counter()
            # Passing None means that the function will get the value from the environment
            keys_metrics_tuples = utils.fill_redis_verbose(aif_characteristics_dict=self.aif_characteristics,
                            AIF_timestamp=self.server_configs['AIF_timestamp'], inference_metrics_dict=self.inference_metrics)
            create_end = time.perf_counter()
            send_start = time.perf_counter()
            try:
                utils.send_redis_verbose(self.my_redis, keys_metrics_tuples)
            except Exception as e:
                self.log(f"Could not send data to Redis: {str(e)}")
            send_end = time.perf_counter()
            create_elapsed_time = create_end - create_start
            send_elapsed_time = send_end - send_start
            self.inference_timings['redis_create'] = create_elapsed_time
            self.inference_timings['redis_send'] = send_elapsed_time
            self.log(f"Redis Create and Send time: {create_elapsed_time * 1000:.2f} ms , {send_elapsed_time * 1000:.2f} ms")
        else:
            self.log('Send Redis Metrics -> False')

    def save_metrics(self):
        """Save metrics on the server, to be requested from the metrics endpoint."""
        start = time.perf_counter()
        self.my_metrics_list.append(utils.create_metric_dictionary(aif_characteristics_dict=self.aif_characteristics,
                            AIF_timestamp=self.server_configs['AIF_timestamp'], inference_metrics_dict=self.inference_metrics))
        end = time.perf_counter()
        elapsed_time = end - start
        self.inference_timings['save_metrics'] = elapsed_time
        self.log(f"Save metrics time: {elapsed_time * 1000:.2f} ms")
    
    def prints(self):
        """Print processing latency and throughput metrics."""
        self.log(' ')
        self.log(f"\tProcessing Latency (data preparation + execution) :  \t{self.inference_metrics['processing_latency']:.2f} ms ({self.inference_metrics['data_preparation_latency']:.2f} + {self.inference_metrics['execution_latency']:.2f})")
        self.log(f"\tTotal throughput (batch size) :                      \t{self.inference_metrics['throughput']:.2f} fps ({self.inference_metrics['batch_size']})")
        
    def platform_preprocess(self, data):
        """Preprocess the input, specific to the platform requirement, not the experiment ones. Must be overridden by {pair}_server.py ({Pair}Server)."""
        raise AssertionError('Forgot to overload platform_preprocess. Must be overridden by {pair}_server.py ({Pair}Server).')

    def platform_postprocess(self, data):
        """Postprocess the output, specific to the platform requirement, not the experiment ones. Must be overridden by {pair}_server.py ({Pair}Server)."""
        raise AssertionError('Forgot to overload platform_postprocess. Must be overridden by {pair}_server.py ({Pair}Server).')

    def log_all_server_values(self):
        """Log all the server values for debugging purposes."""
        self.log(f"{self.server_configs}")
        self.log(f"{self.once_timings}")
        self.log(f"{self.inference_timings}")
        self.log(f"{self.inference_metrics}")
        self.log(f"{self.aif_characteristics}")
