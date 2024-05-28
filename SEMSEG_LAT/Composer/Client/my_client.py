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
import cv2
import numpy as np
import requests
import base_client

class MyClient(base_client.BaseClient):
    def __init__(self, address):
        super().__init__(address)
    
    def send_request(self, url, dataset_path):
        """Defines how the request is sent to the server."""
        # Read the image from the given dataset_path
        img = cv2.imread(dataset_path)
        # Encode the image to a format suitable for sending via HTTP request (in this case, PNG).
        _, img_encoded = cv2.imencode('.png', img)
        # Setting the headers for the POST request
        headers = {'content-type': 'image/jpeg'}
        # Sending the POST request with the dataset attached as a file to the provided URL
        start = time.time()
        response = requests.post(url, data=img_encoded.tobytes(), headers=headers)
        end = time.time()
        # Checking if the server returned a successful response
        if response.status_code != 200:
            raise Exception(f'Inference request failed with status code {response.status_code}')
        # Calculating the latency in seconds
        latency_s = (end-start)
        return response, latency_s

    def manage_response(self, response):
        """Defines how the server's response is handled."""
        seg_img=cv2.imdecode(np.frombuffer(response.content,np.uint8),cv2.IMREAD_COLOR)
        cv2.imwrite(self.output, seg_img)