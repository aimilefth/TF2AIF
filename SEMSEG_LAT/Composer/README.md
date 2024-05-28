# SEMSEG_LAT Composer Flow

## Overview

The Input Directory for the Composer module contains the necessary configuration files, additional libraries, and data required to deploy and execute AI models on various hardware platforms. Each platform has its specific configuration files and libraries to ensure optimal performance and compatibility.

## Directory Structure

```
.
├── Composer
│   ├── AGX
│   │   ├── composer_args_agx.yaml
│   │   └── extra_pip_libraries_agx.txt
│   ├── AGX_TF
│   │   ├── composer_args_agx_tf.yaml
│   │   └── extra_pip_libraries_agx_tf.txt
│   ├── ALVEO
│   │   ├── composer_args_alveo.yaml
│   │   └── extra_pip_libraries_alveo.txt
│   ├── ARM
│   │   ├── composer_args_arm.yaml
│   │   └── extra_pip_libraries_arm.txt
│   ├── ARM_TF
│   │   ├── composer_args_arm_tf.yaml
│   │   └── extra_pip_libraries_arm_tf.txt
│   ├── CPU
│   │   ├── composer_args_cpu.yaml
│   │   └── extra_pip_libraries_cpu.txt
│   ├── CPU_TF
│   │   ├── composer_args_cpu_tf.yaml
│   │   └── extra_pip_libraries_cpu_tf.txt
│   ├── Client
│   │   ├── testing_0.png
│   │   ├── Readme_client.txt
│   │   ├── composer_args_client.yaml
│   │   ├── extra_pip_libraries_client.txt
│   │   └── my_client.py
│   ├── GPU
│   │   ├── composer_args_gpu.yaml
│   │   └── extra_pip_libraries_gpu.txt
│   ├── GPU_TFTRT
│   │   ├── composer_args_gpu_tftrt.yaml
│   │   └── extra_pip_libraries_gpu_tftrt.txt
│   ├── GPU_TF
│   │   ├── composer_args_gpu_tf.yaml
│   │   └── extra_pip_libraries_gpu_tf.txt
│   ├── VERSAL
│   │   ├── composer_args_versal.yaml
│   │   └── extra_pip_libraries_versal.txt
│   ├── ZYNQ
│   │   ├── composer_args_zynq.yaml
│   │   └── extra_pip_libraries_zynq.txt
│   ├── .env
│   ├── composer_args.yaml
│   ├── dockerhub_config.yaml
│   ├── experiment_server.py
│   └── extra_files_dir
│       └── imagenet_class_index.json
```

## File Descriptions

### Global Configuration Files

- **composer_args.yaml**: Contains the general arguments required for the Composer flow, applicable across all AI-framework/platform pairs.
- **dockerhub_config.yaml**: Configuration for Docker Hub to manage image repositories and credentials.
- **experiment_server.py**: Defines the BaseExperimentServer class, which includes methods for handling input decoding, preprocessing, running experiments, postprocessing, and output encoding.
- **.env**: File that contains additional environmental variables required for the final Docker implementation

### AI-framework/platform-Specific Configuration

Each AI-framework/platform directory (e.g., AGX, ALVEO) includes:
- **composer_args_{pair}.yaml**: AI-framework/platform-specific arguments for the Composer flow.
- **extra_pip_libraries_{pair}.txt**: Any additional Python libraries required for the AI-framework/platform.

### Client Directory

- **testing_0.png**: An image for testing.
- **composer_args_client.yaml**: Client-specific arguments for the Composer flow.
- **extra_pip_libraries_client.txt**: Any additional Python libraries required for the client.
- **my_client.py**: Custom client implementation for testing.

## Detailed Descriptions

### `composer_args.yaml`

This file contains general arguments required for the Composer flow, applicable across all platforms. It includes parameters such as application name, network name, network type, focus (throughput or latency), container, platform, model, image, and batch size.

### `dockerhub_config.yaml`

This file includes configuration details for Docker Hub, managing image repositories, and credentials. It ensures that the Docker images are correctly stored and accessed from the specified Docker Hub account.

### `experiment_server.py`

Defines the BaseExperimentServer class, which inherits from the BaseServer class. This class includes several key methods such as initialization, decoding input, encoding output, and sending a response. These methods are consistent across all AI-framework/platform implementations but are specific to a particular experiment implementation.

### `.env`

Contains some environmental variables that should be present on the final 

### AGX Specific Files

#### `AGX/composer_args_agx.yaml`

Contains specific arguments for the AGX platform, including server IP, port, model name, batch size, and calibration file.

#### `AGX/extra_pip_libraries_agx.txt`

Lists additional Python libraries required for the AGX platform.

## Create Your Own Input Directory for Composer Flow

This Composer directory serves as a template for setting up the Composer flow for different AI-framework/platform pairs. Follow these instructions to customize the directory for your specific needs:

### Step-by-Step Guide

1.  **Retain Necessary Subdirectories**:
    - Keep the subdirectories for the AI-framework/platform pairs you need to create. Each subdirectory corresponds to a specific AI-framework/platform pair (e.g., AGX, ALVEO).

2. **Adjust YAML Files**:
    - **Do not remove any `.yaml` files or change the names of their fields**. Instead, adjust their values to match your specific configuration.
    - The `.yaml` files contain essential configuration parameters such as server IP, port, model name, batch size, and other platform-specific settings.

3.  **Implement Custom Logic in `experiment_server.py` and `my_client.py`**:
    - Modify the functions within these files to suit your experiment and client requirements, but do not change their interfaces.
    - Ensure that any changes made to the encoding/decoding logic in `experiment_server.py` are compatible with the corresponding logic in `my_client.py`.

4.  **Extend Docker Container Functionality**:
    - **Additional Files**: Add any required files to the extra_files_dir directory.
    - **Environment Variables**: Define additional environment variables in the .env file. This file can include variables needed for your specific setup, such as API keys, paths, and other configuration details.
    - **Python Libraries**: Specify any extra Python libraries required for your AI-framework/platform in the extra_pip_libraries_{pair}.txt files.

5.  **Prepare AI Model Files** *(if necessary)*:
    - If the Composer flow is to be run without the Converter flow, ensure that the required AI model files are added to the respective AI-framework/platform subdirectories. These model files should be pre-trained and ready for inference.


## Conclusion

The Input Directory for the Composer module is essential for configuring and running AI models on various hardware platforms. By providing AI-framework/platform combination-specific configuration files, additional libraries, and data, it ensures that models are deployed and executed efficiently. This documentation offers a comprehensive overview of the core components and their roles, facilitating an understanding of the Composer flow and its customization for specific AI-framework/platform pairs. The AGX platform serves as a detailed example, providing a template for other AI-framework/platform pairs.