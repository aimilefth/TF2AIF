"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This script converts a TensorFlow 2 SavedModel to a TFLite model for CPU.
The conversion is to FP32, which is optimal for Intel CPU.
The model can be either trained or untrained, purely for inference.

This case doesn't use quantization, therefore trained models don't need datasets.

Main Features:
- Converts TensorFlow 2 SavedModel to TFLite model
- Supports FP32 precision for optimal performance on Intel CPUs
- Can handle both trained and untrained models

Usage:
This script is intended to be run within a Docker container with the necessary environment variables set.

Environment Variables:
- MODELS_PATH: Path to the directory containing the model
- MODEL_NAME: Name of the model to be converted
- TRAINED: Boolean indicating if the model is trained
- DATASETS_PATH: Path to the directory containing datasets (not used in this script)
- DATASET_NAME: Name of the dataset used for quantization (not used in this script)
- OUTPUTS_PATH: Path to the directory where converted models will be saved
- DATALOADERS_PATH: Path to the directory containing dataloaders (not used in this script)
- DATALOADER_NAME: Name of the dataloader script (not used in this script)
- LOG_CONFIG: Path to the logging configuration file
"""

import sys
import tensorflow as tf
import logging
import logging.config
import os
import time

# Define a global constant for the divider string used in logging
DIVIDER = '-------------------------------------------------------------'

def converter(model_path, model_name, output_path):
    """Convert a TensorFlow 2 SavedModel to a TFLite model with FP32 precision."""
    logging.info("Creating Converter")
    # Initialize the TensorFlow Lite converter and load the saved model
    converter = tf.lite.TFLiteConverter.from_saved_model(os.path.join(model_path, model_name))
    logging.info("Starting Conversion")
    # Convert the loaded model to a TensorFlow Lite model
    tflite_model = converter.convert()
    logging.info("Saving TFLite model")
    # Save the converted model to the desired output path
    with open(os.path.join(output_path, model_name + '.tflite'), 'wb') as f:
        f.write(tflite_model)

def strtobool(bool_str):
    """Convert a string representation of a boolean value to its corresponding boolean."""
    return bool_str.lower() in ['true', 'yes', 'y']

def main():
    """Main function to handle the conversion process."""
    # Configure logging settings from an external config file
    logging.config.fileConfig(os.environ['LOG_CONFIG'])
    
    # Log the TensorFlow version for debugging purposes
    logging.info("TF version: {}".format(tf.__version__))
    
    # Parse required parameters from environment variables
    MODEL_PATH = os.environ['MODELS_PATH']
    MODEL_NAME = os.environ['MODEL_NAME']
    TRAINED = strtobool(os.environ['TRAINED'])
    DATASET_PATH = os.environ['DATASETS_PATH']
    DATASET_NAME = os.environ['DATASET_NAME']
    OUTPUT_PATH = os.environ['OUTPUTS_PATH']
    DATALOADERS_PATH = os.environ['DATALOADERS_PATH']
    DATALOADER_NAME = os.environ['DATALOADER_NAME']

    # Log the parsed parameters for reference
    logging.info(' Command line options:')
    logging.info('--model_path         : {}'.format(MODEL_PATH))
    logging.info('--model_name         : {}'.format(MODEL_NAME))
    logging.info('--trained            : {}'.format(TRAINED))
    logging.info('--dataset_path       : {}'.format(DATASET_PATH))
    logging.info('--dataset_name       : {}'.format(DATASET_NAME))
    logging.info('--output_path        : {}'.format(OUTPUT_PATH))
    logging.info('--dataloader_path    : {}'.format(DATALOADERS_PATH))
    logging.info('--dataloader_name    : {}'.format(DATALOADER_NAME))
    logging.info(DIVIDER)

    # Record the start time of the conversion
    global_start_time = time.perf_counter()
    
    # Execute the conversion
    converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH)
    
    # Record the end time of the conversion
    global_end_time = time.perf_counter()
    
    # Log the total time taken for the conversion
    logging.info("Execution Time: %.3f" %(global_end_time - global_start_time))

# Run the main function when the script is executed
if __name__ == '__main__':
    main()
