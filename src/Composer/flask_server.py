#!/usr/bin/python3
"""
Aimilios Leftheriotis
Achilleas Tzenetopoulos
Microlab@NTUA

AI@EDGE project

This module contains the implementation of a Flask server that provides two endpoints for an inference service and a metric service.

The server uses the MyServer class defined in my_server module to handle the actual inference and metric generation tasks.

The logger for the module is configured using the 'LOG_CONFIG' environmental variable. 

There are two main parts of the module:

1. The Flask Application: An instance of the Flask class is created. This instance is used to define the server and the routes it will serve.

2. The Routes: There are two routes defined for this server:

    - '/api/infer': This endpoint accepts POST requests. The input data from these requests is passed to the MyServer instance for inference. The encoded output from the MyServer instance is returned as a response.

    - '/api/metrics': This endpoint also accepts POST requests. It receives a JSON input from the client indicating whether all metrics are to be returned or a specified number of recent metrics. The corresponding metrics are returned as a JSON response.

The server is started with the host and port specified by the 'SERVER_IP' and 'SERVER_PORT' environment variables.

This implementation can serve as a template for building Flask servers for different kinds of machine learning inference services and corresponding metric services.
"""

# Import necessary libraries and modules
import os
import logging
import logging.config
import json
from flask import Flask, request, Response
import uuid
import queue
import threading
# Import custom modules for the server's functionality and utility functions
import my_server
import utils
import time

# Initialize Flask app instance
app = Flask(__name__)
# Single Queue and Condition for both services
request_queue = queue.Queue()
condition = threading.Condition()
results = {}

# Worker function
def worker(logger):

    def get_once_timings_and_num_threads_list(server):
        # Make a deep copy to ensure the original once_timings isn't mutated
        new_dict = server.once_timings.copy()
        # Check if 'NUM_THREADS' exists in server_configs
        if 'NUM_THREADS' in server.server_configs:
            new_dict['NUM_THREADS'] = server.server_configs['NUM_THREADS']
        # Return the new dictionary wrapped in a list
        return [new_dict]

    server = my_server.MyServer(logger)
    while True:
        # Wait for a request to be enqueued
        item = request_queue.get()
        # Process the request
        service_identifier, request_id, request_dict = item
        if service_identifier == 'inference':
            encoded_output = server.inference(indata=request_dict['data'])
            result = server.send_response(encoded_output=encoded_output) 
        elif service_identifier == 'metric':
            # Returns either all metrics or a specified number of recent metrics based on client's request.
            # In this version, add the initialize and warmup times and the NUM_THREADS, if it exists
            once_timings_and_num_threads_list = get_once_timings_and_num_threads_list(server)
            json_input = request_dict['json']
            if(utils.strtobool(json_input['all'])):
                result = Response(response=json.dumps(server.my_metrics_list + once_timings_and_num_threads_list),status=200,mimetype='application/json')
            else:
                number = json_input['number']
                if(isinstance(number, int) and number > 0):
                    result = Response(response=json.dumps(server.my_metrics_list[-number:] + once_timings_and_num_threads_list),status=200,mimetype='application/json')
                else:
                    result = Response(response={'number':'invalid'},status=400,mimetype='application/json')
        # Store the result and notify
        with condition:
            results[request_id] = result
            condition.notify_all()

@app.route('/api/infer', methods=['POST'])
def inference_service():
    """
    Service for performing inference on data received in POST requests.
    Enqueue the request data and return a response immediately.
    """

    request_id = str(uuid.uuid4())
    request_dict = {
        'data': request.data
    }
    # Enqueue the request for processing
    with condition:
        request_queue.put(('inference', request_id, request_dict))
        condition.wait_for(lambda: request_id in results)
    
    # Get the result and return
    result = results.pop(request_id)
    return result

@app.route('/api/metrics', methods=['POST'])
def metric_service():
    """
    Service for fetching metrics based on the parameters received in the POST request.
    Enqueue the request data and return a response immediately.
    """
    json_input = request.get_json()
    request_id = str(uuid.uuid4())
    request_dict = {
        'json': request.get_json()
    }
    # Enqueue the request for processing
    with condition:
        request_queue.put(('metric', request_id, request_dict))
        condition.wait_for(lambda: request_id in results)
    
    # Get the result and return
    result = results.pop(request_id)
    # Get the result as tuple of (stringified json, status)
    #return Response(response=result[0], status=result[1], mimetype='application/json')
    return result

def main():
    # Configure logging based on the environmental variable 'LOG_CONFIG'
    logging.config.fileConfig(os.environ['LOG_CONFIG'], disable_existing_loggers=False)

    # Create logger instances for both logging to file and console
    logger = logging.getLogger('sampleLogger')  # Logger for logging to file
    root_logger = logging.getLogger()  # Logger for logging to console
    # Start the worker thread
    worker_thread = threading.Thread(target=worker, args=(logger,), daemon=True)
    worker_thread.start()
    app.run(host=os.environ['SERVER_IP'], port=int(os.environ['SERVER_PORT'])) # This changes each time depending on the experiment

if __name__ == '__main__':
    main()