# TF2AIF: TensorFlow to AI Framework Conversion and Deployment Tool

## Overview

TF2AIF is a comprehensive tool designed to facilitate the conversion and deployment of AI models across various hardware platforms. It encompasses both conversion of models to different formats and orchestration of inference servers. This repository provides all the necessary scripts, configuration files, and Dockerfiles to streamline these processes.

## Installation

TF2AIF is fully containerized, simplifying the installation process. It has been tested on Ubuntu 18.04 and Ubuntu 20.04 systems. However, it should work on any Linux OS with support for Docker and Docker Buildx. To get started, follow these steps:

1. **Install Docker**:
   - Follow the official Docker installation guide for your operating system: [Docker Installation Guide](https://docs.docker.com/engine/install/)

2. **Enable Docker Buildx**:
   - [Docker Buildx](https://github.com/docker/buildx) is required for building multi-platform images. Enable Docker Buildx by following the instructions below:
   - We recommend using the [manual download](https://github.com/docker/buildx#manual-download) instructions to set up Buildx as the default builder.

3. **Set Up a Multi-platform Builder**:
   - Create a Docker Buildx builder that supports both `linux/amd64` and `linux/arm64` architectures and set it as the default builder. The script below automates this process:

      ```bash
      #!/bin/bash

      # Check if Docker Buildx is installed
      if ! docker buildx version > /dev/null 2>&1; then
         echo "Docker Buildx is not installed. Please install Docker Buildx first."
         exit 1
      fi

      # Remove existing builder instance if it exists
      docker buildx rm multiplat_builder 2>/dev/null || true

      # Create a new builder instance with required architectures
      docker buildx create --name multiplat_builder --driver docker-container --use --platform linux/amd64,linux/arm64

      # Inspect the builder instance
      docker buildx inspect --bootstrap

      # Enable the builder as default
      docker buildx use multiplat_builder
      ```

4. **Verify Docker and Buildx Installation**:
    - Run the following commands to verify that Docker and Buildx are correctly installed and configured:

      ```bash
      docker --version
      docker buildx version
      docker buildx ls
      ```

## Directory Structure

### src

The `src` directory is the core of the TF2AIF project, providing all necessary components for converting and deploying AI models across various hardware platforms.

**Subdirectories:**
- `Base_container_images/`: Dockerfiles and build scripts to create base Docker images for different AI-framework/platform combinations.
- `Composer/`: Scripts and configurations to deploy and run AI models on various hardware platforms.
- `Converter/`: Source code and scripts for the conversion of models to different formats.
- `TF2AIF_runs/`: Scripts to orchestrate the TF2AIF flow for different AI-framework/platform combinations.

For detailed information, see the [src/README.md](src/README.md).

### CLASSIFICATION_THR

This directory demonstrates the full capabilities of the TF2AIF tool for TensorFlow models. It includes data, code, and configuration files to run the TF2AIF flow and generate ResNet50 inference servers for various AI-framework/platform pairs. This directory can also serve as a template for using custom TensorFlow models with the TF2AIF tool.

**Key Files:**
- `TF2AIF_args.yaml`: Configuration file specifying the flow parameters.
- `Converter/`: Contains models, datasets, configurations, and dataloaders for the conversion process.
- `Composer/`: Contains platform-specific configurations and additional libraries for composing the containers.

For detailed information, see the [CLASSIFICATION_THR/README.md](CLASSIFICATION_THR/README.md).


## Usage

### Running the TF2AIF Flow

It is recommended to use the TF2AIF flow by executing the `TF2AIF_runs/TF2AIF_run_all.sh` script located in the `src` directory. This script orchestrates the conversion and composition processes for the specified AI-framework/platform pairs.

#### Example Usage

To run the TF2AIF flow for the CLASSIFICATION_THR example, navigate to the `src/TF2AIF_runs` directory and execute the following command:

```bash
bash TF2AIF_run_all.sh -p ../../CLASSIFICATION_THR -m parallel
```

## Citation

This work has been accepted and will be published in the [2024 EUCNC & 6G Summit](https://www.eucnc.eu/) conference.\
More can be found in our [paper](https://arxiv.org/abs/2404.13715).

If you want to cite this work

```bibtex
@article{leftheriotis2024tf2aif,
  title={TF2AIF: Facilitating development and deployment of accelerated AI models on the cloud-edge continuum},
  author={Leftheriotis, Aimilios and Tzenetopoulos, Achilleas and Lentaris, George and Soudris, Dimitrios and Theodoridis, Georgios},
  journal={arXiv preprint arXiv:2404.13715},
  year={2024}
}
```

## Conclusion

TF2AIF is a powerful tool designed to simplify the conversion and deployment of AI models across various hardware platforms. By following the detailed instructions and utilizing the provided scripts and configuration files, users can efficiently manage the entire workflow from model conversion to deployment.

For more detailed information, refer to the README.md files in the respective directories.

### Additional Resources

[src/Base_container_images/README.md](src/Base_container_images/README.md)\
[src/Composer/README.md](src/Composer/README.md)\
[src/Converter/README.md](src/Converter/README.md)\
[src/TF2AIF_runs/README.md](src/TF2AIF_runs/README.md)\
[CLASSIFICATION_THR/README.md](CLASSIFICATION_THR/README.md)