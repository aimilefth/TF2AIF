"""
BaseClient Documentation

Overview:
=========
The `BaseClient` class is an abstract base class that outlines a generic interface for a client application to communicate with a server running AI tasks. 

The class provides functions for sending requests and managing responses, calculating end-to-end latency and throughput, and outputting the server's metrics in a structured way.

Abstract Methods:
=================
1. send_request(): This method should be implemented in child classes to define how a request is sent to the server. It takes in a url and a path to the dataset.

2. manage_response(): This method should be implemented in child classes to define how the server's response is handled. It takes in a response from the server.

Concrete Methods:
=================
1. ask_inference(): This method sends a request to the server for inference. It calculates the end-to-end latency and throughput based on the server's response.

2. ask_metrics(): This method sends a request to the server for its performance metrics. The server's response is outputted in a structured way.

3. pp_json(): This method pretty prints JSON data. 

This `BaseClient` class is a part of the AI@EDGE project, developed at ICCS, Microlab NTUA.

Contributors:
=============
- Aimilios Leftheriotis
- Achilleas Tzenetopoulos
"""


import os
import time
import requests
import json
import logging

class BaseClient:
    """Abstract base class for a client application to communicate with a server running AI tasks."""
    def __init__(self, address):
        self.address = address
        self.output = os.environ['OUTPUT']

    def send_request(self, url, dataset_path):
        """Defines how the request is sent to the server. Must be overridden by my_client.py (MyClient)."""
        raise AssertionError('Forgot to overload send_request. Must be overridden by my_client.py (MyClient).')

    def manage_response(self, response):
        """Defines how the server's response is handled. Must be overridden by my_client.py (MyClient)."""
        raise AssertionError('Forgot to overload manage_response. Must be overridden by my_client.py (MyClient).')

    def ask_inference(self, dataset_path):
        """Sends a request for inference to the server and calculates latency and throughput."""
        url = self.address + '/api/infer'
        response, latency_s = self.send_request(url, dataset_path)
        dataset_size = int(os.environ['DATASET_SIZE'])
        logging.info('E2E Latency :\t {:.2f} ms'.format(latency_s*1000))
        logging.info('Throughput  :\t {:.2f} fps'.format(dataset_size/latency_s))
        self.manage_response(response)

    def ask_metrics(self, number_of_metrics):
        """Sends a request for performance metrics to the server and outputs them in a structured manner."""
        url = self.address + '/api/metrics'
        content_type = 'application/json'
        headers = {'content-type': content_type}
        # Decide the payload based on number_of_metrics
        json_input = {'all': 'True', 'number': -1} if number_of_metrics == -1 else {'all': 'False', 'number': number_of_metrics}
        start = time.perf_counter()
        # Sending the HTTP POST request with the prepared payload
        response = requests.post(url, json=json_input, headers=headers)
        end = time.perf_counter()
        logging.info('Get Metrics Latency: {:.2f} ms'.format((end-start)*1000))
        metrics_json = response.json()
        self.pp_json(json_thing=metrics_json, sort=False)
        # Writing the JSON data to an output file
        with open(os.environ['METRICS_OUTPUT'], "w") as outfile:
            outfile.write(json.dumps(metrics_json, indent=4))

    def pp_json(self, json_thing, sort=True, indents=4):
        """Pretty prints a JSON string or dict."""
        if type(json_thing) is str:
            print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
        else:
            print(json.dumps(json_thing, sort_keys=sort, indent=indents))
        return None
