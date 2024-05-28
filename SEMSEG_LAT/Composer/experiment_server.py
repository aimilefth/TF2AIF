"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This module defines the BaseExperimentServer class, which inherits from the BaseServer class.
It provides a framework for handling AI inference experiments, including initialization, input decoding, data preprocessing, 
running experiments, postprocessing, and output encoding. These methods are designed to be consistent across different AI-framework/platform 
implementations but can be customized for specific experiments.

Class:
- BaseExperimentServer: Manages the lifecycle of an AI inference experiment, including setup, execution, and response handling.

Methods:
- __init__(self, logger): Initializes the BaseExperimentServer instance and calls the method to set experiment configurations.
- set_experiment_configs(self): Sets up configurations specific to the particular experiment.
- send_response(self, encoded_output): Sends a HTTP response with the encoded output.
- decode_input(self, indata): Decodes the input data from the request.
- create_and_preprocess(self, decoded_input, run_total): Preprocesses the decoded input data, creating a dataset for the experiment.
- postprocess(self, exp_output, run_total): Postprocesses the experiment output.
- encode_output(self, output): Encodes the experiment output for sending in a response.

These methods should be EDITED according to the needs of the specific experiment.
"""

import os
import cv2
import numpy as np
import tensorflow as tf
import time
import json
import zipfile
import shutil
from flask import Response
import io
import contextlib
import tempfile

# Custom module
import base_server

class BaseExperimentServer(base_server.BaseServer):
    def __init__(self, logger):
        """
        Initializes the BaseExperimentServer instance.
        Sets up the experiment configurations and initializes the BaseServer.
        """
        super().__init__(logger)
        self.experiment_configs = {}
        self.set_experiment_configs()
    
    def set_experiment_configs(self):
        """
        Sets up experiment-specific configurations.
        """
        # Important. Set expected input and output shapes to ensure proper resizing.
        self.experiment_configs['expected_input'] = (None, 224, 224, 3)
        self.experiment_configs['expected_output'] = (None, 224, 224, 12)
        CLASSES = {
            "Sky": (128, 64, 128),
            "Wall": (244, 35, 232),
            "Pole": (70, 70, 70),
            "Road": (102, 102, 156),
            "Sidewalk": (190, 153, 153),
            "Vegetation": (153, 153, 153),
            "Sign": (250, 170, 30),
            "Fence": (220, 220, 0),
            "vehicle": (107, 142, 35),
            "Pedestrian": (152, 251, 152),
            "Bicyclist": (70, 130, 180),
            "miscellanea": (220, 20, 60),
            # Fill in the rest of the classes if any
        }
        # Convert RGB values to float32
        COLORS = np.array([color for color in CLASSES.values()], dtype='float32')
        self.experiment_configs['COLORS'] = COLORS

    def send_response(self, encoded_output):
        """
        Sends a HTTP response with the encoded output.
        
        Args:
            encoded_output: The encoded output to be sent in the response.
        
        Returns:
            Response: Flask Response object with the encoded output.
        """
        return Response(response=encoded_output.tobytes(),status=200,mimetype="image/png")

    def decode_input(self, indata):
        """
        Decodes input data from the request.
        Args:
            indata (bytes): The input data from the request. In this implementation, expected to be a zipped dataset of images.
        
        Returns:
            tuple: Decoded input (whichever format) (in this implementation a directory of images) and the total number of data.
        decoded_input becomes the input for create_and_preprocess which also exists on experiment_server.py.
        """
        # Assume we get the data in numpyarray of image encoded bytes
        img=cv2.imdecode(np.frombuffer(indata,np.uint8),cv2.IMREAD_COLOR)
        # Convert BGR to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Set runTotal to 1, since we're processing one image
        runTotal = 1
        decoded_input=img
        return decoded_input, runTotal

    def create_and_preprocess(self, decoded_input, run_total):
        """
        Preprocesses the decoded input data, creating a dataset for the experiment.
        Gets decoded_input from decode_input() and outputs dataset.
        dataset NEEDS to be:
        a) an numpy.array on Latency Server Mode (self.server_configs['SERVER_MODE'] == 0).
        b) a tf.data.Dataset  on Throughput Server Mode (self.server_configs['SERVER_MODE'] == 1).

        Args:
            decoded_input (str): Directory containing the extracted images.
            run_total (int): Total number of images.
        
        Returns:
            dataset: Preprocessed dataset ready for inference.
        """
        def preprocess_image(image):
            image = image.astype(np.float32)
            NORM_FACTOR = 127.5
            image = image / NORM_FACTOR - 1.0
            return image
        x_test = preprocess_image(decoded_input)
        x_test = self.platform_preprocess(x_test)
        dataset = x_test[np.newaxis, :]
        #dataset = x_test
        return dataset

    def postprocess(self, exp_output, run_total):
        """
        Postprocesses the experiment output.
        
        Args:
            exp_output (np.array): Raw output from the experiment.
            run_total (int): Total number of images.
        
        Returns:
            output: Postprocessed output, ready for encoding.
        output becomes the input for encode_output (whichever format fits).
        """
        output = np.argmax(exp_output, axis=3) # Expected shape is (1, HEIGHT, WIDTH) and each index is the number of the color
        return output

    def encode_output(self, output):
        """
        Encodes the processed output.
        Gets the input from postprocess and passes the encoded_output to the send_response function.
        Args:
            output (list): Postprocessed output.
        
        Returns:
            dict: Encoded output ready for sending in a response.
        """
        def give_color_to_seg_img(seg, COLORS):
            # Map each class index in the segmentation map to its corresponding RGB color
            if len(seg.shape) == 3:
                seg = seg[:, :, 0]
            seg_img = np.zeros((seg.shape[0], seg.shape[1], 3)).astype('float')
            # Map the color using the COLORS matrix
            scaled_colors = COLORS / 255.0
            n_classes = len(scaled_colors)
            for c in range(n_classes):
                segc = (seg == c)
                seg_img[:,:,0] += segc * scaled_colors[c, 0]
                seg_img[:,:,1] += segc * scaled_colors[c, 1]
                seg_img[:,:,2] += segc * scaled_colors[c, 2]
            return seg_img
        # Convert the output segmentation map to a color image
        segmentated_image = give_color_to_seg_img(output[0], self.experiment_configs['COLORS'])
        # Convert to 8-bit image for saving to PNG format
        segmentated_image = (segmentated_image*255.0).astype(np.uint8)
        # Encode the segmentation image to PNG format
        _, encoded_output = cv2.imencode('.png', segmentated_image)
        return encoded_output
