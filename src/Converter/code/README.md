# Converter Code Directory

This directory contains the source code and Docker configurations for converting models across various AI-framework/platform pairs. Each subdirectory represents a specific AI-framework/platform pair and includes all necessary files for building Docker images to perform the conversion.

## Supported Conversions

The Converter supports the following AI-framework/platform pairs:

1. **AGX**
   - **TF**: TensorFlow SavedModel to ONNX runtime with TensorRT, INT8
2. **ALVEO**
   - **TF**: TensorFlow SavedModel to ALVEO-specific xmodel for Vitis 1.4.1 framework with INT8
3. **ARM**
   - **TF**: TensorFlow SavedModel to TFLite INT8
4. **CPU**
   - **TF**: TensorFlow SavedModel to TFLite FP32
5. **GPU**
   - **TF**: TensorFlow SavedModel to ONNX runtime with TensorRT, FP32/FP16/INT8

## Directory Structure

Each AI-framework/platform pair has its own subdirectory, which contains the following files:

- `Dockerfile`: The Dockerfile used to build the Docker image for the conversion.
- `README.md`: Documentation specific to the conversion process for that AI-framework/platform pair.
- `converter.py`: The main conversion script that performs the model conversion.
- `logconfig.ini`: The logging configuration file.
- `script.sh`: Additional scripts needed for the conversion process.
- `compiler.sh` (for ALVEO): A script used for model compilation.

## Building Docker Images

Each subdirectory contains a Dockerfile that defines the Docker image for the conversion process. To build the Docker image for a specific AI-framework/platform pair, navigate to the appropriate directory and run:

```shell
docker build -f ./Dockerfile --platform linux/amd64 --tag <your_docker_image_tag> .
```

For example, to build the Docker image for TensorFlow on the AGX platform:

```shell
cd AGX/TF
docker build -f ./Dockerfile --platform linux/amd64 --tag aimilefth/tf2aif_converter:tf_agx .
```
## Running Conversions

To run the conversion for a specific AI-framework/platform pair, execute the corresponding script in the converters directory. For example, for AGX:

```shell
bash converter_agx.sh /path/to/input/Converter TF
```

The script will use the necessary Docker image and perform the conversion based on the input model and specified parameters.
## Key Features

- **Support for Multiple Frameworks**: Converts TensorFlow SavedModel to various formats.
- **Quantization Support**: Allows model quantization using custom datasets.
- **Docker-based Conversion**: Utilizes Docker containers for isolated and consistent conversion environments.
- **Extensible**: Easily add support for new frameworks and platforms by adding new subdirectories and scripts.