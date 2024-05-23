# TF2AIF Runs

This directory contains the scripts necessary to run the TF2AIF flow for different AI-framework/platform combinations. Each subdirectory contains a script named `TF2AIF_run_${pair}.sh` that executes the workflow for the specific AI-framework/platform pair.

## TF2AIF_run_all.sh

The main script to run the TF2AIF flow for all specified AI-framework/platform pairs is `TF2AIF_run_all.sh`. This script can execute the individual `TF2AIF_run_${pair}.sh` scripts either serially or in parallel.

### Usage

To run the TF2AIF flow, navigate to this directory and execute the `TF2AIF_run_all.sh` script with the appropriate arguments:

```bash
bash TF2AIF_run_all.sh -p <relative_path> [-m (serial | parallel)]
```

#### Arguments

-p: The relative path from this directory to the input directory.
-m: Specifies whether to run the TF2AIF_run_${pair}.sh scripts serially or in parallel. Default is serial.

#### Example

For the CLASSIFICATION_THR example, run:

```bash
bash TF2AIF_run_all.sh -p ../../CLASSIFICATION_THR -m parallel
```

### Configuration

The script can be configured by modifying the TF2AIF_args.yaml file located in the input directory (e.g., CLASSIFICATION_THR/TF2AIF_args.yaml). This YAML file specifies various options for the TF2AIF flow.

#### Example TF2AIF_args.yaml

```yaml
input_framework: TF
run_converter: True
run_composer: False
compose_native_TF: False
```

### Modifying AI-Framework/Platform Pairs

To change the AI-framework/platform pairs being executed, modify the arrays *dirs*, and *native_tf_dirs* inside the TF2AIF_run_all.sh script.

### Detailed Script Information

This script orchestrates the execution of individual TF2AIF_run_${pair}.sh scripts. It records the start time, parses input arguments, validates necessary files and variables, and then executes the scripts either serially or in parallel based on the mode specified.

Key Features:

- Supports serial and parallel execution modes.
- Logs output to a file in the logs directory.
- Validates the presence of required files and variables.
- Can extend the directories to process based on configuration options.

### Individual TF2AIF_run_${pair}.sh Scripts

Each AI-framework/platform pair has a corresponding TF2AIF_run_${pair}.sh script. These scripts handle the Corverter and Composer processes for the specific pair.

Example: TF2AIF_run_cpu.sh

This script:

- Validates input arguments.
- Runs the converter if specified.
- Moves files from the converter to the composer and updates YAML files as necessary.
- Runs the composer if specified.
- Logs execution details and calculates elapsed time.

## docker_runs.sh

The `docker_runs.sh` script is used to run a TF2AIF container on a host device with the correct `docker run` commands. This script allows for flexibility in specifying the Docker image, application, device type, and optional environment variables through a YAML file.

### Usage

To use the `docker_runs.sh` script, execute it with the appropriate options:

```bash
bash docker_runs.sh -n <image_name> -a <image_app> -d <device> [-y <yaml_file>]
```

#### Arguments

- -n: The name of the Docker image.
- -a: The application name.
- -d: The type of device on which the container will run. Supported devices are: AGX, ALVEO, ARM, CLIENT, CPU, GPU, AGX_TF, ARM_TF, CPU_TF, GPU_TF.
- -y: (Optional) Path to a YAML file containing environment variables to be passed to the Docker container.

#### Example

```bash
bash docker_runs.sh -n aimilefth/tf2aif_eucnc -a resnet_50 -d GPU -y config.yaml
```

### Script Details

- The script validates the input arguments and ensures that the specified Docker image exists and can be pulled.
- It constructs the Docker run command based on the specified device type and includes any environment variables defined in the YAML file.
- For GPU cases, the script allows specifying a GPU device number through the GPU_DEVICE_NUMBER variable in the YAML file.
- Special handling is included for ALVEO, VERSAL, and ZYNQ devices to mount necessary devices and directories.

### YAML Configuration

If a YAML file is provided, it should define environment variables in the following format:

```yaml
KEY: value
ANOTHER_KEY: another_value
```

#### Example YAML File

```yaml
SERVER_IP: 0.0.0.0
SERVER_IP: 3000
```

### Complete Docker Run Command

Before executing the Docker run command, the script displays the complete command for verification. The command is then executed to start the container with the specified configuration.

### Key Features

- Flexibility: Allows specifying different Docker images, applications, and device types.
- Environment Variables: Supports passing environment variables through a YAML file.
- Device-Specific Handling: Includes special handling for specific device types to ensure proper configuration.

This script ensures that the correct Docker run commands are used to start a TF2AIF container on various supported devices, simplifying the deployment process.

## clean_input.sh


The `clean_input.sh` script is used to clean up specified directories and optionally remove model-related files within a given input path. This helps in resetting the environment by removing logs, outputs, and other temporary files generated during the TF2AIF run, making it easier to prepare for new runs.

### Usage

To use the `clean_input.sh` script, execute it with the appropriate arguments:

```shell
bash clean_input.sh <input_path> [clean_models]
```

#### Arguments

- input_path: The base directory where the logs and other specified directories are located.
- clean_models: (Optional) If set to "True", the script will also clean AI-framework/platform pair directories while preserving certain files. Defaults to "False".

#### Example

```shell
bash clean_input.sh ../../CLASSIFICATION_THR True
```

### Script Details

The clean_input.sh script performs the following steps:

- Check Arguments: Ensures the required input_path argument is provided.
- Set Variables: Sets the input_path and clean_models variables based on provided arguments.
- Remove Directories: Removes specified directories if they exist:
    ${input_path}/logs
    ${input_path}/Converter/logs
    ${input_path}/Converter/outputs
    ${input_path}/Composer/logs
- Clean AI-framework/platform pair directories (if clean_models is "True"):
    Iterates over AI-framework/platform pair directories and preserves specific files while removing others.
- Completion Message: Prints a message indicating the completion of the directory removal process.

### Example Command

To clean the input directory and model directories while preserving configuration files:

```shell
bash clean_input.sh /path/to/input True
```

To clean only the logs and outputs without removing model-related files:

```shell
bash clean_input.sh /path/to/input
```

### Key features
    
- Flexible Cleaning: Allows optional cleaning of model directories.
- Selective Preservation: Preserves important configuration files while cleaning up other files.
- Progress Indication: Provides clear progress messages during the cleaning process.

This script helps maintain a clean working environment by removing unnecessary files and directories, making it easier to reset and prepare for new runs.