"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This script converts a TensorFlow 2 SavedModel to a TFLite model for ARM.
The conversion is to INT8, which is optimal for ARM.
The model can be either trained (requiring a dataset and dataloader) or untrained, purely for inference.
The dataloader needs to be a tf.data.Dataset and should have a batch size of 1.

Main Features:
- Converts TensorFlow 2 SavedModel to TFLite model
- Supports INT8 quantization using calibration data
- Can handle both trained and untrained models
- Utilizes custom dataloaders for quantization

Usage:
This script is intended to be run within a Docker container with the necessary environment variables set.

Environment Variables:
- MODELS_PATH: Path to the directory containing the model
- MODEL_NAME: Name of the model to be converted
- TRAINED: Boolean indicating if the model is trained
- DATASETS_PATH: Path to the directory containing datasets
- DATASET_NAME: Name of the dataset used for quantization
- OUTPUTS_PATH: Path to the directory where converted models will be saved
- DATALOADERS_PATH: Path to the directory containing dataloaders
- DATALOADER_NAME: Name of the dataloader script
- QUANTIZATION_SAMPLES: Number of samples for quantization
- LOG_CONFIG: Path to the logging configuration file
"""

import sys
import tensorflow as tf
import numpy as np
import logging
import logging.config
import os
import time

# Define a global constant for the divider string used in logging
DIVIDER = '-------------------------------------------------------------'

def get_input_shape(model):
    """Extract the input shape from the given model."""
    batched_shape = model.layers[0].input_shape[0]
    logging.info('Model input shape is {}'.format(batched_shape))
    return batched_shape

def get_dtype(model):
    """Extract the data type from the given model."""
    dtype = model.layers[0].input.dtype
    logging.info('Model input dtype is {}'.format(dtype))
    return dtype

def get_random_numpy_input(model, quantization_samples):
    """Generate a random numpy array of the same shape as the model input."""
    input_shape = get_input_shape(model)
    dtype = get_dtype(model)
    random_numpy_shape = (quantization_samples,) + input_shape[1:]
    random_numpy_input = tf.cast(np.random.rand(*random_numpy_shape), dtype=dtype)  # Unpack tuple
    logging.info('Generated random dataset of size {}'.format(random_numpy_input.shape))
    logging.info('Dataset dtype: {}'.format(random_numpy_input.dtype))
    return random_numpy_input

def representative_data_gen_randoms(random_numpy_input, quantization_samples):
    """Generator to produce random input data for model quantization."""
    for input_value in tf.data.Dataset.from_tensor_slices(random_numpy_input).batch(1).take(quantization_samples):
        yield [input_value]

def representative_data_gen_dataloader(ds_quant):
    """Generator to produce input data from a dataloader for model quantization."""
    for input_value in ds_quant:
        yield [input_value]

def trained_converter(model_path, model_name, output_path, dataset_path, dataset_name, dataloader_path, dataloader_name, quantization_samples):
    """Convert a trained model to TFLite with INT8 quantization using a specific dataloader."""
    logging.info("Creating Converter")
    # Initialize the TensorFlow Lite converter and load the saved model
    converter = tf.lite.TFLiteConverter.from_saved_model(os.path.join(model_path, model_name))
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    logging.info("Creating the dataloader")
    sys.path.append(dataloader_path)
    import importlib
    true_dataloader_name = dataloader_name.split('.')[0]  # Get name without .py
    dataloader = importlib.import_module(true_dataloader_name)
    ds_quant = dataloader.get_dataloader(os.path.join(dataset_path, dataset_name), 1, quantization_samples)
    converter.representative_dataset = lambda: representative_data_gen_dataloader(ds_quant)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8
    logging.info("Starting Conversion")
    tflite_model = converter.convert()
    logging.info("Saving TFLite model")
    with open(os.path.join(output_path, model_name + '_int8.tflite'), 'wb') as f:
        f.write(tflite_model)

def converter(model_path, model_name, output_path, quantization_samples):
    """Convert a model to TFLite with INT8 quantization using random data."""
    logging.info("Creating Converter")
    converter = tf.lite.TFLiteConverter.from_saved_model(os.path.join(model_path, model_name))
    model = tf.keras.models.load_model(os.path.join(model_path, model_name))
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    logging.info("Creating Dataset")
    random_numpy_input = get_random_numpy_input(model, quantization_samples)
    converter.representative_dataset = lambda: representative_data_gen_randoms(random_numpy_input, quantization_samples)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8
    logging.info("Starting Conversion")
    tflite_model = converter.convert()
    logging.info("Saving TFLite model")
    with open(os.path.join(output_path, model_name + '_int8.tflite'), 'wb') as f:
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
    QUANTIZATION_SAMPLES = int(os.environ['QUANTIZATION_SAMPLES'])

    # Log the parsed parameters for reference
    logging.info(' Command line options:')
    logging.info('--model_path           : {}'.format(MODEL_PATH))
    logging.info('--model_name           : {}'.format(MODEL_NAME))
    logging.info('--trained              : {}'.format(TRAINED))
    logging.info('--dataset_path         : {}'.format(DATASET_PATH))
    logging.info('--dataset_name         : {}'.format(DATASET_NAME))
    logging.info('--output_path          : {}'.format(OUTPUT_PATH))
    logging.info('--dataloader_path      : {}'.format(DATALOADERS_PATH))
    logging.info('--dataloader_name      : {}'.format(DATALOADER_NAME))
    logging.info('--quantization_samples : {}'.format(QUANTIZATION_SAMPLES))
    logging.info(DIVIDER)

    # Record the start time of the conversion
    global_start_time = time.perf_counter()

    # Use the appropriate converter function based on whether the model is trained and the precision required
    if(TRAINED):
        trained_converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, DATASET_PATH, DATASET_NAME, DATALOADERS_PATH, DATALOADER_NAME, QUANTIZATION_SAMPLES)
    else:
        converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, QUANTIZATION_SAMPLES)
    
    # Record the end time of the conversion
    global_end_time = time.perf_counter()

    # Log the total time taken for the conversion
    logging.info("Execution Time: %.3f" %(global_end_time - global_start_time))

# Run the main function when the script is executed
if __name__ == '__main__':
    main()
