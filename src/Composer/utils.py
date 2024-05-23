'''
Aimilios Leftheriotis
Achilleas Tzenetopoulos
Microlab@NTUA

AI@EDGE project

Useful functions. Mostly used for RedisTimeSeries monitoring and the metric_service functionality.
'''

from dotenv import load_dotenv
from pathlib import Path
from redistimeseries.client import Client
import os
import time


class LimitedList(list):
    """
    Extends the list class to create a fixed-size First In First Out (FIFO) list.
    Items appended beyond the max size automatically push out the oldest items.
    Used on the metrics service.
    """
    def __init__(self, max_size):
        self.max_size = max_size
        super().__init__()

    def append(self, item):
        super().append(item)
        if len(self) > self.max_size:
            self.pop(0)

metric_dictionary = {
    # All the relevant fields of the metric dictionary. Used on the metrics service.

    'app_name':str,
    'network_name':str,
    'network_type':str,
    'device':str,
    'focus':str,
    'AIF_timestamp':int,
    'processing_latency':float,
    'data_preparation_latency':float,
    'execution_latency':float,
    'throughput':float,
    'dataset_size': int,
    'batch_size':int,
    'app_UID':str,
    'instance_UID':str,
    'timestamp':int,
    'node_name':str
}

def read_node_env_variables():
    """Load node-specific environmental variables on /scrape/.env. Reads the address of the RedisTimeSeries. Used on the monitoring."""
    dotenv_path = Path('/scrape/.env')
    load_dotenv(dotenv_path=dotenv_path)

def create_redis():
    """
    Establishes a connection to the RedisTimeSeries database using environmental variables.
    Returns a client for interactions with the RedisTimeSeries.
    Used on the monitoring.
    """
    rts = Client(
        host=os.getenv('REDIS_IP', '127.0.0.1'),
        port=int(os.getenv('REDIS_PORT', '6379'))
    )
    return rts

def fill_redis_verbose(aif_characteristics_dict,
                       AIF_timestamp, inference_metrics_dict):
    """
    Prepares key-metric tuples based on the provided AI characteristics and inference metrics.
    These tuples are then used to send data to RedisTimeSeries.
    Used on the monitoring.
    """
    keys_metrics_tuples = []
    app_name = aif_characteristics_dict['app_name']
    network_name = aif_characteristics_dict['network_name']
    network_type = aif_characteristics_dict['network_type']
    device = aif_characteristics_dict['device']
    focus = aif_characteristics_dict['focus']
    app_UID = app_name + ':' + network_name + ':' + network_type + ':' + device + ':' + focus
    instance_UID = app_UID + ':' + str(AIF_timestamp)
    key = "AIF:" + instance_UID
    keys_metrics_tuples.append((key+":"+'processing_latency', inference_metrics_dict['processing_latency']))
    keys_metrics_tuples.append((key+":"+'data_preparation_latency', inference_metrics_dict['data_preparation_latency']))
    keys_metrics_tuples.append((key+":"+'execution_latency', inference_metrics_dict['execution_latency']))
    keys_metrics_tuples.append((key+":"+'throughput', inference_metrics_dict['throughput']))
    keys_metrics_tuples.append((key+":"+'dataset_size', inference_metrics_dict['dataset_size']))
    keys_metrics_tuples.append((key+":"+'batch_size', inference_metrics_dict['batch_size']))
    return keys_metrics_tuples

def send_redis_verbose(rts, keys_metrics_tuples):
    """Sends the provided metric data to RedisTimeSeries with the current timestamp. Used on the monitoring."""
    timestamp = int(time.perf_counter()*1000)
    for key_metric_tuple in keys_metrics_tuples:
        rts.add(key_metric_tuple[0], timestamp, key_metric_tuple[1])

def create_metric_dictionary(aif_characteristics_dict,
                             AIF_timestamp, inference_metrics_dict):
    """
    Populates a metric dictionary with relevant data based on AI characteristics and inference metrics.
    Returns the populated metric dictionary. This will be stored on the metrics list.
    Used on the metrics service.
    """
    my_dict = {}
    my_dict['app_name'] = aif_characteristics_dict['app_name']
    my_dict['network_name'] = aif_characteristics_dict['network_name']
    my_dict['network_type'] =aif_characteristics_dict['network_type']
    my_dict['device'] = aif_characteristics_dict['device']
    my_dict['focus'] = aif_characteristics_dict['focus']
    my_dict['AIF_timestamp'] = AIF_timestamp
    my_dict['processing_latency'] = inference_metrics_dict['processing_latency']
    my_dict['data_preparation_latency'] = inference_metrics_dict['data_preparation_latency']
    my_dict['execution_latency'] = inference_metrics_dict['execution_latency']
    my_dict['throughput'] = inference_metrics_dict['throughput']
    my_dict['dataset_size'] = inference_metrics_dict['dataset_size']
    my_dict['batch_size'] = inference_metrics_dict['batch_size']
    my_dict['app_UID'] = my_dict['app_name'] + ':' + my_dict['network_name'] + ':' + my_dict['network_type'] + ':' + my_dict['device'] + ':' + my_dict['focus']
    my_dict['instance_UID'] = my_dict['app_UID'] + ':' + str(my_dict['AIF_timestamp'])
    my_dict['node_name'] = os.getenv('NODE_NAME', 'ai-at-edge-worker-01')
    my_dict['timestamp'] = int(time.perf_counter()*1000)
    return my_dict

def strtobool(bool_str):
    """Converts string representations of truthiness to boolean values."""
    my_bool = bool_str.lower() in ['true', 'yes', 'y']
    return my_bool

def decode_server_mode(server_mode):
    """
    Maps string representations of server modes to their numerical representations.
    E.g., 'latency' becomes 0 and 'throughput' becomes 1.
    Used to decide the self.server_configs['SERVER_MODE'].
    """
    my_server_mode = server_mode.lower()
    if my_server_mode in ['lat', 'latency']:
        return 0
    elif my_server_mode in ['thr', 'throughput']:
        return 1