# Composer Flow

## Overview

The Composer module is designed to facilitate the deployment and execution of AI models on various hardware platforms. Each platform has its specific server implementation, Dockerfile, and configuration scripts to ensure optimal performance and compatibility. This documentation covers the base functionality and specific implementations for the AGX platform, as an example AI-framework/platform pair.

## Directory Structure

```
.
├── AGX
│   ├── Dockerfile.agx
│   ├── agx_server.py
│   ├── composer_agx.sh
│   └── my_server.py
├── base_server.py
├── flask_server.py
├── utils.py
```

### File Descriptions

#### Base Files

- **base_server.py**: Provides the foundational server functionality consistent across all platforms.
- **flask_server.py**: Manages the Flask web server to handle incoming requests and route them to the appropriate server methods.
- **utils.py**: Contains utility functions for RedisTimeSeries monitoring and metric service functionality.

#### AGX Directory

- **Dockerfile.agx**: Defines the Docker image for the AGX platform.
- **agx_server.py**: Implements the AGX-specific server functionality by extending the base server class.
- **composer_agx.sh**: Script to build and run the AGX Docker container.
- **my_server.py**: Contains AGX-specific extensions and overrides for server operations.

## Detailed Descriptions

### `base_server.py`

The BaseServer class provides the core functionality for managing AI model inference workflows. It includes methods for:

- Initializing server configurations, metrics, and AI characteristics.
- Logging.
- Redis connection handling.
- Managing the inference workflow (decoding input, preprocessing, running experiments, postprocessing, and encoding output).
- Calculating and logging benchmark metrics.

### `flask_server.py`

This file manages the Flask web server, which is responsible for handling incoming HTTP requests. It routes these requests to the appropriate server methods for processing and returns the results to the client. The server is designed to be lightweight and efficient, ensuring minimal overhead during request handling.

### `utils.py`

Provides utility functions for handling RedisTimeSeries and metric service functionality.

### `AGX/agx_server.py`

The {Pair}Server class extends the BaseServer to implement {pair}-specific functionality. In the case of AgxServer, it is optimized for running ONNX Runtime models on AGX hardware. Key functionalities include:

- Initializing the AI-model using the appropriate APIs for each AI-framework/platform pair. AgxServer initializes the ONNX Runtime inference session with TensorRT and CUDA execution providers.
-Performing a warm-up run to ensure the server is ready for handling inference requests.
-Executing single or multiple inference experiments based on the server mode (latency or throughput).
-Handling {pair}-specific preprocessing and postprocessing steps.

### `AGX/my_server.py`

This file creates a my_server class that inherits all the functionality from the appropriate {Pair}Server class (AgxServer) and is called by the flask_server.py.

### `AGX/Dockerfile.agx`

The `Dockerfile.agx` defines the Docker image for the AGX platform. It includes all necessary dependencies and environment setup required to run the AGX-specific server. The Dockerfile ensures that the environment is consistent and replicable across different deployments.

### `AGX/composer_agx.sh`

The `composer_agx.sh` script orchestrates the Composer flow for the AGX platform. It includes steps to set up the Docker environment and build the image using the appropriate Base_container_image. This script simplifies the deployment process, making it easy to set up and run the Composer on the AGX platform.


## Usage

It is generally recommended to use the Composer flow as part of the TF2AIF flow by executing the appropriate `TF2AIF_run.sh` scripts, with `TF2AIF_run_all.sh` being the preferred option for running all scripts collectively. However, it is also possible to run the Composer flow individually.

To run the Composer flow for a specific AI-framework/platform pair, execute the corresponding script in the appropriate `{pair}` subdirectory. For example, for the AGX platform, you would run:

```shell
bash converter_agx.sh /path/to/input/Composer /path/to/src/Composer
```

This script performs the following steps:

- **File and Variable Check**: Verifies the presence of all required files and environment variables.
- **File Preparatio**n: Copies necessary files to the working directory.
- **Docker Image Build**: Builds the Docker image using the specified Dockerfile and build arguments.
- **Docker Image Push**: Pushes the built image to the specified Docker repository.
- **Cleanup**: Removes temporary files to maintain a clean working directory.

Before running the script, prepare the Input Directory. Specifically, ensure that the Composer subdirectory of the Input Directory is correctly implemented with all necessary configuration files, additional libraries, and data required for your specific AI-framework/platform pair.

## Conclusion

The Composer flow is a robust and flexible framework for deploying and running AI models on a variety of AI-framework/platform combinations. By leveraging platform-specific configurations and Docker containers, it ensures that models are executed efficiently and effectively. The AGX platform serves as a prime example of how the Composer can be tailored to different hardware, providing a template for other AI-framework/platform pairs. This documentation provides a comprehensive overview of the core components and their roles, facilitating an understanding of the Composer flow and its customization for specific platforms.