"""
Author: Aimilios Leftheriotis, Achilleas Tzenetopoulos
Affiliations: Microlab@NTUA, VLSILab@UPatras

This module provides various utility functions used for RedisTimeSeries monitoring and the metric service functionality
within the AI@EDGE project.

Overview:
- The LimitedList class: A fixed-size First In First Out (FIFO) list for storing metrics.
- Metric dictionary structure: Defines the relevant fields used in the metrics service.
- Functions for environment variable management, Redis connection, metric data preparation, and sending metrics to Redis.
"""

from dotenv import load_dotenv
from pathlib import Path
from redistimeseries.client import Client
import os
import time

class LimitedList(list):
    """
    Extends the list class to create a fixed-size First In First Out (FIFO) list.
    Items appended beyond the max size automatically push out the oldest items.
    Used in the metrics service.
    """
    def __init__(self, max_size):
        self.max_size = max_size
        super().__init__()

    def append(self, item):
        super().append(item)
        if len(self) > self.max_size:
            self.pop(0)

metric_dictionary = {
    # All the relevant fields of the metric dictionary. Used in the metrics service.
    'app_name': str,
    'network_name': str,
    'network_type': str,
    'device': str,
    'focus': str,
    'AIF_timestamp': int,
    'processing_latency': float,
    'data_preparation_latency': float,
    'execution_latency': float,
    'throughput': float,
    'dataset_size': int,
    'batch_size': int,
    'app_UID': str,
    'instance_UID': str,
    'timestamp': int,
    'node_name': str
}

def read_node_env_variables():
    """
    Load node-specific environmental variables from /scrape/.env.
    Reads the address of the RedisTimeSeries.
    Used in monitoring.
    """
    dotenv_path = Path('/scrape/.env')
    load_dotenv(dotenv_path=dotenv_path)

def create_redis():
    """
    Establish a connection to the RedisTimeSeries database using environmental variables.
    Returns a client for interactions with the RedisTimeSeries.
    Used in monitoring.
    """
    rts = Client(
        host=os.getenv('REDIS_IP', '127.0.0.1'),
        port=int(os.getenv('REDIS_PORT', '6379'))
    )
    return rts

def fill_redis_verbose(aif_characteristics_dict, AIF_timestamp, inference_metrics_dict):
    """
    Prepare key-metric tuples based on the provided AI characteristics and inference metrics.
    These tuples are then used to send data to RedisTimeSeries.
    Used in monitoring.
    """
    keys_metrics_tuples = []
    app_name = aif_characteristics_dict['app_name']
    network_name = aif_characteristics_dict['network_name']
    network_type = aif_characteristics_dict['network_type']
    device = aif_characteristics_dict['device']
    focus = aif_characteristics_dict['focus']
    app_UID = f"{app_name}:{network_name}:{network_type}:{device}:{focus}"
    instance_UID = f"{app_UID}:{AIF_timestamp}"
    key = f"AIF:{instance_UID}"
    keys_metrics_tuples.append((f"{key}:processing_latency", inference_metrics_dict['processing_latency']))
    keys_metrics_tuples.append((f"{key}:data_preparation_latency", inference_metrics_dict['data_preparation_latency']))
    keys_metrics_tuples.append((f"{key}:execution_latency", inference_metrics_dict['execution_latency']))
    keys_metrics_tuples.append((f"{key}:throughput", inference_metrics_dict['throughput']))
    keys_metrics_tuples.append((f"{key}:dataset_size", inference_metrics_dict['dataset_size']))
    keys_metrics_tuples.append((f"{key}:batch_size", inference_metrics_dict['batch_size']))
    return keys_metrics_tuples

def send_redis_verbose(rts, keys_metrics_tuples):
    """
    Send the provided metric data to RedisTimeSeries with the current timestamp.
    Used in monitoring.
    """
    timestamp = int(time.perf_counter() * 1000)
    for key, metric in keys_metrics_tuples:
        rts.add(key, timestamp, metric)

def create_metric_dictionary(aif_characteristics_dict, AIF_timestamp, inference_metrics_dict):
    """
    Populate a metric dictionary with relevant data based on AI characteristics and inference metrics.
    Returns the populated metric dictionary. This will be stored in the metrics list.
    Used in the metrics service.
    """
    app_UID = f"{aif_characteristics_dict['app_name']}:{aif_characteristics_dict['network_name']}:{aif_characteristics_dict['network_type']}:{aif_characteristics_dict['device']}:{aif_characteristics_dict['focus']}"
    my_dict = {
        'app_name': aif_characteristics_dict['app_name'],
        'network_name': aif_characteristics_dict['network_name'],
        'network_type': aif_characteristics_dict['network_type'],
        'device': aif_characteristics_dict['device'],
        'focus': aif_characteristics_dict['focus'],
        'AIF_timestamp': AIF_timestamp,
        'processing_latency': inference_metrics_dict['processing_latency'],
        'data_preparation_latency': inference_metrics_dict['data_preparation_latency'],
        'execution_latency': inference_metrics_dict['execution_latency'],
        'throughput': inference_metrics_dict['throughput'],
        'dataset_size': inference_metrics_dict['dataset_size'],
        'batch_size': inference_metrics_dict['batch_size'],
        'app_UID': app_UID,
        'instance_UID': f"{app_UID}:{AIF_timestamp}",
        'node_name': os.getenv('NODE_NAME', 'ai-at-edge-worker-01'),
        'timestamp': int(time.perf_counter() * 1000)
    }
    return my_dict

def strtobool(bool_str):
    """
    Convert string representations of truthiness to boolean values.
    Used to interpret configuration strings.
    """
    return bool_str.lower() in ['true', 'yes', 'y']

def decode_server_mode(server_mode):
    """
    Map string representations of server modes to their numerical representations.
    E.g., 'latency' becomes 0 and 'throughput' becomes 1.
    Used to set the self.server_configs['SERVER_MODE'] in BaseServer.
    """
    mode = server_mode.lower()
    if mode in ['lat', 'latency']:
        return 0
    elif mode in ['thr', 'throughput']:
        return 1
