# TF2AIF Source Directory

## Overview

The TF2AIF project is designed to facilitate the conversion and deployment of AI models across various hardware platforms. The source directory (`src`) is structured to support both the conversion of models to different formats and the orchestration of inference servers. This directory contains scripts, configuration files, and Dockerfiles to streamline these processes.

## Directory Structure

```
.
├── Base_container_images
├── Composer
├── Converter
└── TF2AIF_runs
```

### Base_container_images

This directory provides Dockerfiles and build scripts to create base Docker images for different AI-framework/platform combinations. These images are optimized for frameworks such as TensorFlow (TF) across various hardware platforms including AGX, ALVEO, ARM, CPU, and GPU.

**Files:**
- `Dockerfile`: Instructions to build the Docker image.
- `docker_build.sh`: Script to build and push the Docker image.

For detailed information, see the [Base_container_images/README.md](Base_container_images/README.md).

### Composer

The Composer module is responsible for deploying and running AI models on various hardware platforms. Each AI-framework/platform combination has specific server implementations, Dockerfiles, and scripts to ensure optimal performance and compatibility.

**Files:**
- `base_server.py`: Core functionality for managing AI model inference workflows.
- `flask_server.py`: Manages the Flask web server to handle HTTP requests.
- `utils.py`: Utility functions for handling RedisTimeSeries and metric services.
- AI-framework/platform combination-specific subdirectories (e.g., AGX, ARM) with their respective Dockerfiles and scripts.

For detailed information, see the [Composer/README.md](Composer/README.md).

### Converter

The Converter module converts input models into various framework formats for different AI-framework/platform pairs. It supports TensorFlow (TF) SavedModel formats as inputs and allows for model quantization using custom datasets.

**Files:**
- `code`: Source code for creating Docker images for model conversion.
- `converters`: Scripts to run the Docker containers for conversion.
- Configuration files for specific conversions.

For detailed information, see the [Converter/README.md](Converter/README.md).

### TF2AIF_runs

This directory contains scripts to run the TF2AIF flow for different AI-framework/platform combinations. It includes scripts for both individual and collective execution of the conversion and composition processes.

**Files:**
- `TF2AIF_run_all.sh`: Main script to run the TF2AIF flow for all specified AI-framework/platform pairs.
- `docker_runs.sh`: Script to run a TF2AIF container on a host device.
- `clean_input.sh`: Script to clean up specified directories and optionally remove model-related files.
- Platform-specific subdirectories with their respective run scripts (e.g., TF2AIF_run_agx.sh).

For detailed information, see the [TF2AIF_runs/README.md](TF2AIF_runs/README.md).

## Usage

### Running the TF2AIF Flow

It is recommended to use the TF2AIF flow by executing the `TF2AIF_runs/TF2AIF_run_all.sh` script. This script orchestrates the conversion and composition processes for the specified AI-framework/platform pairs.

#### Example Usage

To run the TF2AIF flow for the CLASSIFICATION_THR example, navigate to the `TF2AIF_runs` directory and execute the following command:

```bash
bash TF2AIF_run_all.sh -p ../../CLASSIFICATION_THR -m parallel
```

### Cleaning Up

Use the `clean_input.sh` script to clean up logs, outputs, and other temporary files generated during the TF2AIF run.

#### Example Usage

For the CLASSIFICATION_THR example, navigate to the `TF2AIF_runs` directory and execute the following command:

```bash
bash clean_input.sh ../../CLASSIFICATION_THR True
```

## Conclusion

The `src` directory is the core of the TF2AIF project, providing all necessary components for converting and deploying AI models across various hardware platforms. By following the detailed instructions and utilizing the provided scripts and configuration files, users can efficiently manage the entire workflow from model conversion to deployment.

For more detailed information, refer to the README.md files in the respective subdirectories.

### Additional Resources

- [Base_container_images/README.md](Base_container_images/README.md)
- [Composer/README.md](Composer/README.md)
- [Converter/README.md](Converter/README.md)
- [TF2AIF_runs/README.md](TF2AIF_runs/README.md)

This documentation provides a comprehensive guide to understanding and utilizing the TF2AIF project, ensuring a smooth workflow for converting and deploying AI models.
