# TF2AIF Run CPU_TF

This directory contains the `TF2AIF_run_cpu_tf.sh` script, which is used to execute the TF2AIF workflow for the CPU_TF AI-framework/platform pair. The script handles the composition processes for the specified input framework.

## TF2AIF_run_cpu_tf.sh

The `TF2AIF_run_cpu_tf.sh` script automates the execution of the TF2AIF workflow for the CPU_TF AI-framework/platform pair. It performs the following tasks:

1. Moves files from the Converter to the Composer and updates YAML files as necessary.
2. Runs the Composer if specified.

### Usage

To use the `TF2AIF_run_cpu_tf.sh` script, execute it with the appropriate arguments:

```shell
bash TF2AIF_run_cpu_tf.sh <absolute_input_path> <run_converter> <run_composer> <SRC_DIR> <input_framework>
```

#### Arguments

- absolute_input_path: The absolute path to the input directory.
- run_converter: Whether to run the converter (True/False).
- run_composer: Whether to run the composer (True/False).
- SRC_DIR: The source directory where the converter and composer scripts are located.
- input_framework: The input framework (e.g., TF, PT).

#### Example

```shell
bash TF2AIF_run_cpu_tf.sh /path/to/input True True /path/to/src TF
```

### Functionality

- **Initial Checks**:
  - Ensures the script receives exactly five arguments. If not, it prints the usage information and exits.

- **Logging**:
  - Creates the logs directory if it doesn't exist.
  - Directs the output to a log file in the logs directory.
  - Prints the current date and time when the script starts.

- **Move Files and Update YAMLs**:
  - If both `run_converter` and `run_composer` are set to "True", the script moves the TensorFlow model to the Composer directory and updates the Composer YAML files.
  - It moves the directory containing the SavedModel and updates the corresponding YAML argument (`MODEL_NAME_ARG`).

- **Run Composer**:
  - If `run_composer` is set to "True", the script checks if the Composer directory exists and runs the composer script for the CPU_TF AI-framework/platform pair.
  - If the directory doesn't exist, it prints an error message.

- **Completion**:
  - Calculates the elapsed time and prints the execution time.

### Key Features

- **Automated Workflow**: Automates the execution of the TF2AIF workflow for the CPU_TF AI-framework/platform pair.
- **Flexible Configuration**: Allows specifying whether to run the converter.
- **Logging**: Provides detailed logging of the script's execution.
- **File Management**: Moves converted files and updates YAML configurations as needed.

### Example Command

To run the TF2AIF workflow for the CPU_TF AI-framework/platform pair:

```shell
bash TF2AIF_run_cpu_tf.sh /path/to/input True True /path/to/src TF
```

This script helps in streamlining the process of running the TF2AIF workflow for the CPU_TF AI-framework/platform pair by automating the necessary steps and providing detailed logging and error handling.
