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
        self.experiment_configs['expected_output'] = (None, 1000)
        CLASS_INDEX_JSON = os.environ['CLASS_INDEX_JSON']
        with open(CLASS_INDEX_JSON) as f:
            self.experiment_configs['CLASS_INDEX'] = json.load(f)
        
        # Create a temporary directory for storing the dataset.
        self.experiment_configs['temp_dataset_dir'] = tempfile.mkdtemp()
        
        # Set image size and shape configurations.
        self.experiment_configs['image_size'] = (224, 224)
        self.experiment_configs['image_shape'] = (self.server_configs['BATCH_SIZE'], 224, 224, 3)
        
    def send_response(self, encoded_output):
        """
        Sends a HTTP response with the encoded output.
        
        Args:
            encoded_output: The encoded output to be sent in the response.
        
        Returns:
            Response: Flask Response object with the encoded output.
        """
        return Response(response=json.dumps(encoded_output), status=200, mimetype="application/json")
    
    def decode_input(self, indata):
        """
        Decodes input data from the request.
        Args:
            indata (bytes): The input data from the request. In this implementation, expected to be a zipped dataset of images.
        
        Returns:
            tuple: Decoded input (whichever format) (in this implementation a directory of images) and the total number of data.
        decoded_input becomes the input for create_and_preprocess which also exists on experiment_server.py.
        """
        # Extract the zip contents to a temporary dataset directory.
        zip_ref = zipfile.ZipFile(io.BytesIO(indata), 'r')
        zip_ref.extractall(self.experiment_configs['temp_dataset_dir'])
        zip_ref.close()
        
        # Get the folder name containing the extracted images.
        foldername = os.path.join(self.experiment_configs['temp_dataset_dir'], os.listdir(self.experiment_configs['temp_dataset_dir'])[0])
        
        # List and sort all image files in the folder.
        listimage = os.listdir(foldername)
        listimage.sort()
        
        self.experiment_configs['listimage'] = listimage
        runTotal = len(listimage)
        decoded_input = foldername
        
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
        def preprocess(image):
            # Preprocess images using ResNet50 preprocessing function.
            image = tf.keras.applications.resnet50.preprocess_input(image)
            return image

        # Suppress stdout to avoid unwanted print messages.
        with open(os.devnull, 'w') as devnull:
            with contextlib.redirect_stdout(devnull):
                ds_val = tf.keras.preprocessing.image_dataset_from_directory(
                    directory=decoded_input,
                    labels=None,
                    label_mode=None,
                    color_mode="rgb",
                    batch_size=self.server_configs['BATCH_SIZE'],
                    image_size=self.experiment_configs['image_size'],
                    shuffle=False
                )
        
        # Additional preprocessing steps.
        ds_val = ds_val.map(lambda x: preprocess(x))
        ds_val = ds_val.map(lambda x: self.platform_preprocess(x))
        dataset = ds_val
        
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
        def softmax(logits):
            # Compute softmax for 2D arrays.
            scores = logits - np.max(logits, axis=1, keepdims=True)
            e_x = np.exp(scores.astype(np.float64))
            return e_x / np.sum(e_x, axis=1, keepdims=True)

        def decode_predictions(preds, top=5):
            """
            Decode the top N predicted classes (e.g., ImageNet classes).
            tf.keras.applications.imagenet_utils.decode_predictions.
            CLASS_INDEX must come from imagenet_class_index.json.
            """
            results = []
            for pred in preds:
                top_indices = pred.argsort()[-top:][::-1]
                result = [(int(i), self.experiment_configs['CLASS_INDEX'][str(i)][1], pred[i]) for i in top_indices]
                result.sort(key=lambda x: x[2], reverse=True)
                results.append(result)
            return results
        
        preds = []
        # Add platform_postprocess before everything else
        platform_output = self.platform_postprocess(exp_output)
        probs = softmax(platform_output)
        preds.extend(decode_predictions(probs, top=5))
        
        output = preds
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
        # Convert the postprocessed output into a dictionary.
        out_dict = {}
        for i in range(len(output)):
            out_dict[self.experiment_configs['listimage'][i]] = output[i]
        
        # Cleanup by removing the temporary dataset directory.
        shutil.rmtree(self.experiment_configs['temp_dataset_dir'], ignore_errors=True)
        
        encoded_output = out_dict
        return encoded_output
