"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This script converts a TensorFlow 2 SavedModel to a .xmodel format for ALVEO.
The conversion is to INT8, which is optimal for ALVEO.
The model can be either trained (requiring a dataset and dataloader) or untrained, purely for inference.
The dataloader needs to be a tf.data.Dataset and should have a batch size of 1.
The model should be in TF2 SavedModel format from <=TF2.3.

Main Features:
- Converts TensorFlow 2 SavedModel to .xmodel format
- Supports INT8 quantization using calibration data
- Can handle both trained and untrained models
- Utilizes custom dataloaders for quantization
- Handles ALVEO-specific requirements

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
- ARCH: Architecture specification for ALVEO (e.g., u280_l, u280_h)
- LOG_CONFIG: Path to the logging configuration file
"""

import sys
import tensorflow as tf
import numpy as np
import logging
import logging.config
import os
import time
from tensorflow_model_optimization.quantization.keras import vitis_quantize
import shutil
import tempfile
import subprocess

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

def get_dataset_randoms(random_numpy_input, quantization_samples):
    """Convert random data into a TensorFlow Dataset (tf.data.Dataset)."""
    return tf.data.Dataset.from_tensor_slices(random_numpy_input).batch(1).take(quantization_samples)

def trained_converter(model_path, model_name, output_path, dataset_path, dataset_name, dataloader_path, dataloader_name, quantization_samples, arch):
    """Convert a trained model to .xmodel with INT8 quantization using a specific dataloader."""
    logging.info("Creating Converter")
    model = tf.keras.models.load_model(os.path.join(model_path, model_name))
    logging.info('Creating the dataloader')
    sys.path.append(dataloader_path)
    import importlib
    true_dataloader_name = dataloader_name.split('.')[0]  # Get name without .py
    dataloader = importlib.import_module(true_dataloader_name)
    ds_quant = dataloader.get_dataloader(os.path.join(dataset_path, dataset_name), 1, quantization_samples)
    logging.info('Creating Quantizer')
    quantizer = vitis_quantize.VitisQuantizer(model)
    logging.info('Running Quantizer')
    quantized_model = quantizer.quantize_model(calib_dataset=ds_quant)
    logging.info('Saving quantized .h5 model')
    Q_MODEL_PATH = tempfile.mkdtemp()
    Q_MODEL_NAME = 'q_temp.h5'
    quantized_model.save(os.path.join(Q_MODEL_PATH, Q_MODEL_NAME))
    logging.info('Running Compiler')
    run_compiler(model_name, output_path, Q_MODEL_PATH, Q_MODEL_NAME, arch)
    shutil.rmtree(Q_MODEL_PATH, ignore_errors=True)

def converter(model_path, model_name, output_path, quantization_samples, arch):
    """Convert a model to .xmodel with INT8 quantization using random data."""
    logging.info("Creating Converter")
    logging.info("TF version: {}".format(tf.__version__))
    model = tf.keras.models.load_model(os.path.join(model_path, model_name))
    random_numpy_input = get_random_numpy_input(model, quantization_samples)
    ds_quant = get_dataset_randoms(random_numpy_input, quantization_samples)
    logging.info('Creating Quantizer')
    quantizer = vitis_quantize.VitisQuantizer(model)
    logging.info('Running Quantizer')
    quantized_model = quantizer.quantize_model(calib_dataset=ds_quant)
    logging.info('Saving quantized .h5 model')
    Q_MODEL_PATH = tempfile.mkdtemp()
    Q_MODEL_NAME = 'q_temp.h5'
    os.makedirs(Q_MODEL_PATH, exist_ok=True)
    quantized_model.save(os.path.join(Q_MODEL_PATH, Q_MODEL_NAME))
    logging.info('Running Compiler')
    # Compile quantized model to .xmodel
    run_compiler(model_name, output_path, Q_MODEL_PATH, Q_MODEL_NAME, arch)
    shutil.rmtree(Q_MODEL_PATH, ignore_errors=True)

def run_compiler(model_name, output_path, q_model_path, q_model_name, arch):
    """Compile the quantized model to .xmodel format."""
    q_model_path_name = os.path.join(q_model_path, q_model_name)
    log_file = os.getenv('LOG_FILE', 'AIF_log') + '_' + os.getenv('MODEL_NAME', 'default_model') + '.log'
    compiler_name = os.environ['COMPILER']
    command = './' + compiler_name + ' -n ' + model_name + ' -o ' + output_path + ' -q ' + q_model_path_name + ' -a ' + arch.lower() + ' -l ' + log_file
    try:
        if sys.version_info >= (3, 7):
            result = subprocess.run(command, check=True, capture_output=True, universal_newlines=True, shell=True)
        else:
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('command "{}" return with error (code {}): {}'.format(e.cmd, e.returncode, e.output))

def assert_correct_arch(arch):
    """Ensure the provided ALVEO arch is valid."""
    correct_list = ['u280_l', 'u280_h']
    if(arch.lower() not in correct_list):
        raise AssertionError ('Incorrect arch environmental variable, got {}'.format(arch))

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
    ARCH = os.environ['ARCH']

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
    logging.info('--arch                 : {}'.format(ARCH))
    logging.info(DIVIDER)

    # Record the start time of the conversion
    global_start_time = time.perf_counter()

    # Use the appropriate converter function based on whether the model is trained and the precision required
    assert_correct_arch(ARCH)
    if(TRAINED):
        trained_converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, DATASET_PATH, DATASET_NAME, DATALOADERS_PATH, DATALOADER_NAME, QUANTIZATION_SAMPLES, ARCH)
    else:
        converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, QUANTIZATION_SAMPLES, ARCH)

    # Record the end time of the conversion
    global_end_time = time.perf_counter()

    # Log the total time taken for the conversion
    logging.info('Execution Time: %.3f' %(global_end_time - global_start_time))

# Run the main function when the script is executed
if __name__ == '__main__':
    main()
