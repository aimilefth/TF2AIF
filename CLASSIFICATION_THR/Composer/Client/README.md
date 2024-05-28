# Client Directory Documentation

## Overview

This directory contains the client-side implementation for communicating with the server running AI tasks. The client is responsible for sending datasets for inference, managing responses from the server, and requesting performance metrics. This is part of the AI@EDGE project.

## File Descriptions

### Experiment-Specific Files

1. **dockerhub_config.yaml**: Choose the image name and label.

### Server-Specific Files

1. **my_client.py**: Contains platform-specific server code.
2. **docker_build_args_client.yaml**: Contains platform-specific Docker build arguments.
3. **Add your dataset**: Ensure your dataset is included in the appropriate directory.

## Docker Build Instructions

To build the Docker image for the client, use the appropriate Client TF2AIF flow or Composer flow scripts.

## Docker Run Command
To run the Docker container on the host, use the [docker_runs.sh](src/TF2AIF_runs/docker_runs.sh) script as follows:

```bash
bash docker_runs.sh -n <image_name> -a <image_app> -d CLIENT [-y <yaml_file>]
```

### Arguments
- `-n`: The name of the Docker image.
- `-a`: The application name.
- `-d`: The type of device on which the container will run. For the client, use CLIENT.
- `-y`: (Optional) Path to a YAML file containing environment variables to be passed to the Docker container.

#### Example

```bash
bash docker_runs.sh -n aimilefth/tf2aif_refactor -a class_thr -d CLIENT -y client_config.yaml
```

### YAML Configuration

If a YAML file is provided, it should define environment variables in the following format:

```yaml
KEY: value
ANOTHER_KEY: another_value

```

#### Example YAML File

```yaml
SERVER_IP: 192.168.1.228
SERVER_PORT: 3000

```

## Execution on Container 

Running the Client Docker container, initialized a bash terminal. For more information on how to run the Client, refer to [src/Composer/Client/README.md](src/Composer/Client/README.md).

### Execute on Container to Get Inference

To execute on the container and get inference, run the following command:

```bash
python3 ${CLIENT_APP}
```

Or:

```bash
python3 client.py
```

### Execute on Container to Get Metrics in JSON Format

To execute on the container and get metrics in JSON format, run the following command:

```bash
python3 ${CLIENT_APP} -m True
```

## Environment Variables

The following environment variables can be set to manage the client:

- **SERVER_IP**: The IP address of the server.
- **SERVER_PORT**: The port of the server.

Ensure these environment variables are correctly set to allow the client to communicate with the server.

## Conclusion

This directory provides the necessary tools and instructions for setting up and running the client-side application for the AI@EDGE project. By following the provided steps and ensuring the correct configuration, you can effectively communicate with the server, perform inference tasks, and gather performance metrics.
