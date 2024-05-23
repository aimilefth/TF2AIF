# Converter

This directory contains the source code and scripts for the Converter flow. It converts input models into various framework formats for different AI-framework/platform pairs. The Converter supports TensorFlow (TF) SavedModel model formats as inputs.

## Supported Conversions

1. **AGX**
   - ONNX runtime with TensorRT, INT8
   - Formats: `.onnx`
2. **ALVEO**
   - ALVEO-specific xmodel for Vitis 1.4.1 framework with INT8
   - Formats: `.xmodel`
3. **ARM**
   - TFLite INT8
   - Formats: `.tflite`
4. **CPU**
   - TFLite FP32
   - Formats: `.tflite`
5. **GPU**
   - ONNX runtime with TensorRT, FP32/FP16/INT8
   - Formats: `.onnx`

The tool supports the quantization of models using custom datasets, wherever this is needed.

## Repository Structure

1. **code directory**
   - Contains subdirectories for each AI-framework/platform pair, which include the source code needed to create Docker images that implement the conversions.
   - Each subdirectory follows this structure:
     - `converter.py`: The main conversion script.
     - `Dockerfile`: Dockerfile to create the conversion environment.
     - `logconfig.ini`: Logging configuration file.
     - `README.md`: Documentation for the specific converter.
     - `script.sh`: Additional scripts for conversion.

2. **converters directory**
   - Contains subdirectories for each AI-framework/platform pair, which include the converter scripts to run the Docker containers.
   - Each subdirectory follows this structure:
     - `converter_{pair}.sh`: Shell script to run the converter Docker container.

## Input Directory Structure

The input directory must contain the Converter directory, which in turn must contain the following additional directories for correct functionality:

1. **models**
   - Contains the input model (either a TF SavedModel or PT model).
2. **configurations**
   - Contains the YAML configuration files that control the Converter flow.
3. **dataset**
   - Contains datasets needed for quantization (optional).
4. **dataloaders**
   - Contains the code needed to feed the dataset into the tool correctly (preprocessed `tf.data.Dataset`) (optional).

### Example tree of an input_directory/Converter (CLASSIFICATION_THR/Converter)

```
Converter/
├── configurations
│   ├── AGX
│   │   └── converter_args_agx.yaml
│   ├── ALVEO
│   │   └── converter_args_alveo.yaml
│   ├── ARM
│   │   └── converter_args_arm.yaml
│   ├── CPU
│   │   └── converter_args_cpu.yaml
│   ├── GPU
│   │   └── converter_args_gpu.yaml
│   └── converter_args.yaml
├── dataloaders *(optional)*
│   ├── my_imagenet_dataloader.py
│   └── resnet50_dataloader.py
├── datasets *(optional)*
│   └── ImageNet_val_100
|        └── *many image files*
└── models
    └── ResNet50_ImageNet_70_90_7_76GF_2_3
        ├── assets
        ├── saved_model.pb
        └── variables
            ├── variables.data-00000-of-00001
            └── variables.index
```

## Usage

It is generally recommended to use the Converter flow as part of the TF2AIF flow by executing the appropriate `TF2AIF_run.sh` scripts, with `TF2AIF_run_all.sh` being the preferred option for running all scripts collectively. However, it is also possible to run the Converter flow individually.

To run the conversion for a specific AI-framework/platform pair, execute the corresponding script in the `converters` directory. For example, AGX:

```shell
bash converter_agx.sh /path/to/input/Converter TF
```

The script will build the necessary Docker image and perform the conversion based on the input model and specified parameters.

## Example

Assuming the input model is a TF SavedModel located at `/path/to/input/Converter/models`, the conversion for the AGX platform can be initiated as follows:

```shell
bash converter_agx.sh /path/to/input/Converter TF
```

The output model will be saved in the appropriate directory (/path/to/input/Converter/outputs/AGX).

## Key Features

- **Support for Multiple Frameworks**: Converts TF SavedModel to various formats.
- **Quantization Support**: Allows model quantization using custom datasets.
- **Docker-based Conversion**: Utilizes Docker containers for isolated and consistent conversion environments.
- **Extensible**: Easily add support for new frameworks and platforms by adding new subdirectories and scripts.
