"""
Author: Aimilios Leftheriotis
Affiliations: Microlab@NTUA, VLSILab@UPatras

This script converts a TensorFlow 2 SavedModel to an ONNX model ready to be powered by 
TensorRT Execution Provider or CUDA Execution Provider. The model can be either trained 
(requiring a dataset and dataloader) or untrained, purely for inference. The dataloader 
needs to be a tf.data.Dataset.

Main Features:
- Converts TensorFlow 2 SavedModel to ONNX model
- Supports INT8 quantization using calibration data
- Can handle both trained and untrained models
- Utilizes custom dataloaders for quantization

Usage:
This script is intended to be run within a Docker container with the necessary environment 
variables set.

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
- BATCH_SIZE: Batch size used during conversion
- PRECISION: Desired precision for the converted model. Currently only INT8 is supported.
- LOG_CONFIG: Path to the logging configuration file
"""

import sys
import tensorflow as tf
import numpy as np
import logging
import logging.config
import os
import time
import tf2onnx
import subprocess
import onnx
import shutil
import tempfile
from onnxruntime.quantization import create_calibrator, write_calibration_table
from onnxruntime.quantization import CalibrationDataReader

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

def get_random_numpy_input(model, batch_size, quantization_samples):
    """Generate a random numpy array of the same shape as the model input."""
    input_shape = get_input_shape(model)
    dtype = get_dtype(model)
    random_numpy_shape = (quantization_samples * batch_size,) + input_shape[1:]
    random_numpy_input = tf.cast(np.random.rand(*random_numpy_shape), dtype=dtype)  # Unpack tuple
    logging.info('Generated random dataset of size {}'.format(random_numpy_input.shape))
    logging.info('Dataset dtype: {}'.format(random_numpy_input.dtype))
    return random_numpy_input

def get_dataset_randoms(random_numpy_input, batch_size, quantization_samples):
    """Convert random data into a TensorFlow Dataset (tf.data.Dataset)."""
    return tf.data.Dataset.from_tensor_slices(random_numpy_input).batch(batch_size).take(quantization_samples)

def trained_int8_converter(model_path, model_name, output_path, batch_size, precision, dataset_path, dataset_name, dataloader_path, dataloader_name, quantization_samples):
    """Convert a trained TF model to ONNX with INT8 quantization using a specific dataloader."""
    logging.info("Creating Converter")
    model = tf.keras.models.load_model(os.path.join(model_path, model_name))
    input_shape = get_input_shape(model)
    shape = (batch_size,) + input_shape[1:]
    logging.info('Converting TF model to ONNX model')
    spec = (tf.TensorSpec(shape, tf.float32, name="input"),)
    output_name = f"{model_name}_{precision}_{batch_size}.onnx"
    onnx_model = tf2onnx.convert.from_keras(model=model, input_signature=spec, output_path=os.path.join(output_path, output_name))
    logging.info("Model saved at {}".format(os.path.join(output_path, output_name)))

    # Create a temporary directory for the ONNX model
    ONNX_MODEL_PATH = tempfile.mkdtemp()
    ONNX_MODEL_NAME = output_name

    # Import the specified dataloader
    logging.info('Creating the dataloader')
    sys.path.append(dataloader_path)
    import importlib
    true_dataloader_name = dataloader_name.split('.')[0]  # Get name without .py
    dataloader = importlib.import_module(true_dataloader_name)    
    ds_quant = dataloader.get_dataloader(os.path.join(dataset_path, dataset_name), batch_size, quantization_samples)
    
    logging.info('Creating Calibrator')
    calibrator = create_calibrator(os.path.join(output_path, output_name), [], augmented_model_path=os.path.join(ONNX_MODEL_PATH, ONNX_MODEL_NAME))
    calibrator.set_execution_providers(["CPUExecutionProvider"])
    
    logging.info("Creating Data Reader")
    data_reader = MyCalibrationDataReader(ds_quant=ds_quant)
    
    logging.info("Collecting Data")
    calibrator.collect_data(data_reader)
    
    logging.info("Creating Calibration Table")
    write_calibration_table(calibrator.compute_range())
    
    logging.info('Moving Calibration Table')
    CALIBRATION_NAME = f"{model_name}_{precision}_{batch_size}.flatbuffers"
    subprocess.Popen("mv {} {}".format("calibration.flatbuffers", os.path.join(output_path, CALIBRATION_NAME)), shell=True)
    logging.info("Calibration table saved at {}".format(os.path.join(output_path, CALIBRATION_NAME)))

    shutil.rmtree(ONNX_MODEL_PATH, ignore_errors=True)

def int8_converter(model_path, model_name, output_path, batch_size, precision, quantization_samples):
    """Convert a TF model to ONNX with INT8 quantization using random data."""
    logging.info("Creating Converter")
    model = tf.keras.models.load_model(os.path.join(model_path, model_name))
    input_shape = get_input_shape(model)
    shape = (batch_size,) + input_shape[1:]
    logging.info('Converting TF model to ONNX model')
    spec = (tf.TensorSpec(shape, tf.float32, name="input"),)
    output_name = f"{model_name}_{precision}_{batch_size}.onnx"
    onnx_model = tf2onnx.convert.from_keras(model=model, input_signature=spec, output_path=os.path.join(output_path, output_name))
    logging.info("Model saved at {}".format(os.path.join(output_path, output_name)))

    # Create a temporary directory for the ONNX model
    ONNX_MODEL_PATH = tempfile.mkdtemp()
    ONNX_MODEL_NAME = output_name

    logging.info('Creating random dataset')
    random_numpy_input = get_random_numpy_input(model, batch_size, quantization_samples)
    ds_quant = get_dataset_randoms(random_numpy_input, batch_size, quantization_samples)
    
    logging.info('Creating Calibrator')
    calibrator = create_calibrator(os.path.join(output_path, output_name), [], augmented_model_path=os.path.join(ONNX_MODEL_PATH, ONNX_MODEL_NAME))
    calibrator.set_execution_providers(["CPUExecutionProvider"])
    
    logging.info("Creating Data Reader")
    data_reader = MyCalibrationDataReader(ds_quant=ds_quant)
    
    logging.info("Collecting Data")
    calibrator.collect_data(data_reader)
    
    logging.info("Creating Calibration Table")
    write_calibration_table(calibrator.compute_range())
    
    logging.info('Moving Calibration Table')
    CALIBRATION_NAME = f"{model_name}_{precision}_{batch_size}.flatbuffers"
    subprocess.Popen("mv {} {}".format("calibration.flatbuffers", os.path.join(output_path, CALIBRATION_NAME)), shell=True)
    logging.info("Calibration table saved at {}".format(os.path.join(output_path, CALIBRATION_NAME)))

    shutil.rmtree(ONNX_MODEL_PATH, ignore_errors=True)

def converter(model_path, model_name, output_path, batch_size, precision):
    """Convert a TF model to ONNX."""
    logging.info("Creating Converter")
    model = tf.keras.models.load_model(os.path.join(model_path, model_name))
    input_shape = get_input_shape(model)
    shape = (batch_size,) + input_shape[1:]
    logging.info("Input shape is {}".format(shape))
    logging.info('Converting TF model to ONNX model')
    spec = (tf.TensorSpec(shape, tf.float32, name="input"),)
    output_name = f"{model_name}_{precision}_{batch_size}.onnx"
    onnx_model = tf2onnx.convert.from_keras(model=model, input_signature=spec, output_path=os.path.join(output_path, output_name))
    logging.info("Model saved at {}".format(os.path.join(output_path, output_name)))

def assert_correct_precision(precision):
    """Ensure the provided precision is valid."""
    correct_list = ['int8', 'fp16', 'fp32']
    if(precision.lower() not in correct_list):
        raise AssertionError(f'Incorrect precision environmental variable, got {precision}')

def strtobool(bool_str):
    """Convert a string representation of a boolean value to its corresponding boolean."""
    return bool_str.lower() in ['true', 'yes', 'y']

class MyCalibrationDataReader(CalibrationDataReader):
    """Custom calibration data reader class."""
    def __init__(self, ds_quant):
        self.ds_quant = ds_quant
        self.ds_quant_iterator = iter(self.ds_quant)

    def get_next(self):
        inputs = next(self.ds_quant_iterator, None)
        if(inputs is None):
            return None
        else:
            return {'input': inputs.numpy()}

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
    BATCH_SIZE = int(os.environ['BATCH_SIZE'])
    PRECISION = os.environ['PRECISION']

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
    logging.info('--batch_size           : {}'.format(BATCH_SIZE))
    logging.info('--precision            : {}'.format(PRECISION))
    logging.info(DIVIDER)

    # Record the start time of the conversion
    global_start_time = time.perf_counter()

    # Use the appropriate converter function based on whether the model is trained and the precision required
    assert_correct_precision(PRECISION)
    if(TRAINED and PRECISION == 'INT8'):
        trained_int8_converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, BATCH_SIZE, PRECISION, DATASET_PATH, DATASET_NAME, DATALOADERS_PATH, DATALOADER_NAME, QUANTIZATION_SAMPLES)
    elif(PRECISION == 'INT8'):
        int8_converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, BATCH_SIZE, PRECISION, QUANTIZATION_SAMPLES)
    else:
        converter(MODEL_PATH, MODEL_NAME, OUTPUT_PATH, BATCH_SIZE, PRECISION)

    # Record the end time of the conversion
    global_end_time = time.perf_counter()

    # Log the total time taken for the conversion
    logging.info("Execution Time: %.3f" %(global_end_time - global_start_time))

# Run the main function when the script is executed
if __name__ == '__main__':
    main()