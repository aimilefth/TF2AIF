#!/usr/bin/python3
"""
Authors: Aimilios Leftheriotis, Achilleas Tzenetopoulos
Affiliations: Microlab@NTUA, VLSILab@UPatras

This module implements a Flask server that provides endpoints for AI model inference and metric services.

Overview:
- The Flask server is configured to handle two primary services: 
  1. Inference Service
  2. Metric Service
- It utilizes the MyServer class from the my_server module to process the requests.
- The server is designed to be lightweight and efficient, ensuring minimal overhead during request handling.

Functionality:
1. Inference Service ('/api/infer'):
   - Accepts POST requests with input data for inference.
   - Enqueues the request for asynchronous processing.
   - Returns the encoded output from the MyServer instance as the response.

2. Metric Service ('/api/metrics'):
   - Accepts POST requests with parameters to fetch metrics.
   - Enqueues the request for asynchronous processing.
   - Returns either all metrics or a specified number of recent metrics based on the client's request.

Logging:
- The logging configuration is specified by the 'LOG_CONFIG' environment variable.
- The module sets up loggers for both file and console output.

Queue and Threading:
- A single queue is used to manage requests for both services.
- A worker thread processes the requests from the queue.
- Condition variables are used to synchronize request processing and result retrieval.

Usage:
- The server is started with the host and port specified by the 'SERVER_IP' and 'SERVER_PORT' environment variables.
- This implementation can serve as a template for building Flask servers for various machine learning inference and metric services.

Note:
- The server is designed to work with AI-framework/platform pair-specific server classes, which should be defined in their respective modules (e.g., {pair}_server.py).

This module can be extended and customized to support additional services or integrate with different AI models and platforms.
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
import my_server  # Import custom modules for the server's functionality and utility functions
import utils

# Initialize Flask app instance
app = Flask(__name__)
# Single Queue and Condition for both services
request_queue = queue.Queue()
condition = threading.Condition()
results = {}

# Worker function to process requests
def worker(logger):
    """
    Worker thread to process inference and metric requests.
    """
    def get_once_timings_and_num_threads_list(server):
        """
        Retrieve the once_timings and NUM_THREADS from the server and return as a list.
        """
        new_dict = server.once_timings.copy()
        if 'NUM_THREADS' in server.server_configs:
            new_dict['NUM_THREADS'] = server.server_configs['NUM_THREADS']
        return [new_dict]

    server = my_server.MyServer(logger)
    while True:
        # Wait for a request to be enqueued
        item = request_queue.get()
        service_identifier, request_id, request_dict = item
        if service_identifier == 'inference':
            encoded_output = server.inference(indata=request_dict['data'])
            result = server.send_response(encoded_output=encoded_output) 
        elif service_identifier == 'metric':
            once_timings_and_num_threads_list = get_once_timings_and_num_threads_list(server)
            json_input = request_dict['json']
            if utils.strtobool(json_input['all']):
                result = Response(response=json.dumps(server.my_metrics_list + once_timings_and_num_threads_list), status=200, mimetype='application/json')
            else:
                number = json_input['number']
                if isinstance(number, int) and number > 0:
                    result = Response(response=json.dumps(server.my_metrics_list[-number:] + once_timings_and_num_threads_list), status=200, mimetype='application/json')
                else:
                    result = Response(response={'number': 'invalid'}, status=400, mimetype='application/json')
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
    request_dict = {'data': request.data}
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
    request_dict = {'json': json_input}
    # Enqueue the request for processing
    with condition:
        request_queue.put(('metric', request_id, request_dict))
        condition.wait_for(lambda: request_id in results)
    # Get the result and return
    result = results.pop(request_id)
    return result

def main():
    """
    Main function to configure logging, start the worker thread, and run the Flask app.
    """
    # Configure logging based on the environmental variable 'LOG_CONFIG'
    logging.config.fileConfig(os.environ['LOG_CONFIG'], disable_existing_loggers=False)

    # Create logger instances for both logging to file and console
    logger = logging.getLogger('sampleLogger')  # Logger for logging to file
    root_logger = logging.getLogger()  # Logger for logging to console

    # Start the worker thread
    worker_thread = threading.Thread(target=worker, args=(logger,), daemon=True)
    worker_thread.start()

    # Run the Flask app with specified host and port
    app.run(host=os.environ['SERVER_IP'], port=int(os.environ['SERVER_PORT']))

if __name__ == '__main__':
    main()
