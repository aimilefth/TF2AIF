# Converters

This directory contains the scripts to run the Docker containers for converting models to different formats for various AI-framework/platform pairs. Each script sets up the necessary environment, checks for required files and directories, and runs the conversion process in a Docker container.

## Usage

To run the conversion for a specific AI-framework/platform pair, execute the corresponding script. For example:

```shell
bash converter_{pair}.sh /path/to/input/converter TF
```

### Arguments

- **converter_path**: The Converter directory of the input directory, where the models, configurations, datasets, and dataloaders directories are located.
- **input_framework**: The framework of the input model (e.g., TF).

### Example

```shell
bash converter_agx.sh /absolute/path/to/CLASSIFICATION_THR TF
```

## Functionality

- **Initial Checks**:
  - Ensures the script receives exactly two arguments. If not, it prints the usage information and exits.

- **Logging**:
  - Creates the logs and outputs directories if they don't exist.
  - Directs the output to a log file in the logs directory.
  - Prints the current date and time when the script starts.

- **Configuration Loading**:
  - Loads configuration variables from YAML files (`converter_args_{pair}.yaml` and `converter_args.yaml`).

- **Directory and File Validation**:
  - Checks for the existence of required directories and files.
  - Validates necessary environment variables.

- **Docker Run**:
  - Constructs the Docker run command with appropriate volume mounts and environment variables.
  - Executes the conversion process in the Docker container.

- **Completion**:
  - Calculates the elapsed time and prints the execution time.

## Example Command

To run the conversion for the AGX platform:

```shell
bash converter_agx.sh /path/to/input/Converter TF
```

This script helps in streamlining the process of converting models for different platforms by automating the necessary steps and providing detailed logging and error handling.

## Input Directory Structure

The input directory must contain the Converter directory, which in turn must contain the following additional directories for correct functionality:

1. **models**
   - Contains the input model (a TF SavedModel).
2. **configurations**
   - Contains the YAML configuration files that control the Converter flow.
3. **dataset**
   - Contains datasets needed for quantization (optional).
4. **dataloaders**
   - Contains the code needed to feed the dataset into the tool correctly (preprocessed `tf.data.Dataset`) (optional).

Example tree of an input_directory/Converter (CLASSIFICATION_THR/Converter)

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

Each converter loads the environmental variables that configure the Docker container from the `converter_args_{pair}.yaml` and `converter_args.yaml` files. The required environmental variables depend on the AI-framework/platform pair and the input framework.

## Key Features

- **Automated Conversion**: Automates the conversion process for various AI-framework/platform pairs.
- **Flexible Configuration**: Allows specifying the input framework and paths.
- **Logging**: Provides detailed logging of the script's execution.
- **File Management**: Validates the existence of necessary files and directories.
