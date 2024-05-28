"""
MyClient Documentation

Overview:
=========
The `MyClient` class extends the `BaseClient` class, implementing the methods specific to its usage. 
This client sends images for inference to a server and handles the server's response. 

Class Methods:
==============
1. __init__(self, address): Inherits from the `BaseClient` class, initializing with an address to connect to.

2. send_request(url, dataset_path): Encodes a dataset from the dataset path and sends a POST request to the server at the specified url. 
   The function measures the time taken to get the response and returns the response along with the time taken.

3. manage_response(response): Decodes the server's response to retrieve the desired output. Then, the output is saved/processed.

This `MyClient` class is a part of the AI@EDGE project, developed at ICCS, Microlab NTUA.

Contributors:
=============
- Aimilios Leftheriotis
- Achilleas Tzenetopoulos
"""

import os
import time
import json
import requests
import base_client

class MyClient(base_client.BaseClient):
    """
    Client class for sending images for inference to a server and handling the server's response.
    Inherits from BaseClient and implements methods specific to this usage.
    """
    def __init__(self, address):
        """Initialize the MyClient instance with an address to connect to."""
        super().__init__(address)
    
    def send_request(self, url, dataset_path):
        """
        Defines how the request is sent to the server.
        Encodes the dataset from the provided path and sends a POST request to the server.

        Parameters:
        - url (str): The URL to send the POST request to.
        - dataset_path (str): The path to the dataset file.

        Returns:
        - response: The server's response.
        - latency_s (float): The time taken to get the response in seconds.
        """
        # Open the dataset from the provided path in binary read mode
        with open(dataset_path, 'rb') as file:
            fileobj = file.read()
        
        # Set the headers for the POST request
        headers = {'Content-Type': 'application/zip'}
        
        # Send the POST request with the dataset attached as a file to the provided URL
        start = time.time()
        response = requests.post(url, data=fileobj, headers=headers)
        end = time.time()
        
        # Check if the server returned a successful response
        if response.status_code != 200:
            raise Exception(f'Inference request failed with status code {response.status_code}')
        
        # Calculate the latency in seconds
        latency_s = end - start
        return response, latency_s

    def manage_response(self, response):
        """
        Defines how the server's response is handled.
        Decodes the server's response to retrieve the desired output and saves the output to a file.

        Parameters:
        - response: The server's response.
        """
        response_data = json.loads(response.content)
        with open(self.output, 'w') as outfile:
            outfile.write(json.dumps(response_data, indent=4))
