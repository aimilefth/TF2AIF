# Client Directory Documentation

## Overview

The `Client` directory contains the client-side implementation for communicating with the server running AI tasks. The client is responsible for sending datasets for inference, managing responses from the server, and requesting performance metrics.

## Directory Structure

```
.
├── base_client.py
├── client.py
├── composer_client.sh
├── Dockerfile.client
├── docker_run_client_metrics.sh
├── logconfig.ini
└── metrics_script.py
```

## Detailed File Descriptions

### `base_clinet.py`

This file defines the `BaseClient` class, an abstract base class that outlines a generic interface for a client application to communicate with a server running AI tasks. The class provides methods for sending requests, managing responses, calculating end-to-end latency and throughput, and outputting the server's metrics in a structured way.

### `client.py`

This script serves as the client application. It constructs a command-line argument parser to interpret user-provided arguments, enabling the client to either request performance metrics from the server or send a dataset for inference. The script then creates an instance of MyClient, an extension of the BaseClient class, to execute the specified operations. Through MyClient, the application can seamlessly switch between querying the server for metrics and performing inference tasks, ensuring a flexible and robust client-server interaction.

#### Command Line Arguments:

- **--dataset_path**: Path of the dataset (default from `DATASET` environment variable).
- **--address**: Address to connect to (default from `SERVER_IP` and `SERVER_PORT` environment variables).
- **--ask_metrics**: Flag to indicate whether to request performance metrics from the server instead of performing inference (default is False).
- **--number_of_metrics**: Specifies the number of metrics to retrieve from the server (-1 means all, default is -1).

### 'composer_client.sh'

The `composer_client.sh` script orchestrates the Composer flow for the Client. It includes steps to set up the Docker environment and build the image using the appropriate Base_container_image. This script simplifies the deployment process.

### `Dockerfile.client`

The `Dockerfile.client` defines the Docker image for the Client. It includes all necessary dependencies and environment setup required to run the Client application. The Dockerfile ensures that the environment is consistent and replicable across different deployments.

### `metrics_script.py`

This script is used to automate the process of running multiple inference requests and collecting performance metrics from the server. It ensures that the client can send requests and retrieve metrics in a loop, handling retries and formatting the output appropriately.

### `docker_run_client_metrics.sh`

The `docker_run_client_metrics.sh` script is designed to automate the process of running multiple client instances in Docker containers, each targeting different servers for collecting performance metrics. This script ensures that the specified servers are running, sends a defined number of requests, and collects the metrics data from each server.

#### How It Works

1. **Initialization and Input Parameters**:
    - The script takes four arguments:
        - `REPO_NAME`: The name of the Docker repository.
        - `IMAGE_NAME`: The name of the Docker image.
        - `METRICS_DIR`: The directory where the metrics data will be stored.
        - `NUMBER_OF_REQUESTS`: The number of requests each client should send to the server.

2. **Server Details**:
    - The `data` array holds the directories, IP addresses, and ports for different servers. Each set of three values corresponds to one server configuration.

3. **IP and Port Validation**:
    - Functions `is_valid_ip` and `is_valid_port` are defined to validate the format of the IP addresses and ports.
    - The script iterates over the data array, validating each IP and port. It also checks for duplicate IP/port combinations to avoid conflicts.

4. **Running Client Containers**:
    - The script declares an associative array `pids` to store the process IDs (PIDs) of the background Docker container processes along with their corresponding directory names.
    - It iterates over the `data` array in steps of three (directory, IP, port) and runs a Docker container for each server configuration in the background using the `setsid` command.
    - The Docker containers are named using the `METRICS_DIR` and the lowercase directory name. They are run with the environment variables `NUMBER_OF_REQUESTS`, `SERVER_IP`, and `SERVER_PORT` set appropriately. The `metrics_script.py` is executed inside the containers to collect the metrics.

5. **Monitoring and Cleanup**:
    - The script enters a loop that checks the status of the running Docker containers. It uses the `kill -0` command to check if a process is still running.
    - If a process has finished, the script prints a message indicating the completion of the metrics collection for that specific server and removes the corresponding PID from the `pids` array.
    - The loop continues until all processes have completed.

#### Usage

To run the script, execute the following command:

```bash
bash docker_run_client_metrics.sh <REPO_NAME> <IMAGE_NAME> <METRICS_DIR> <NUMBER_OF_REQUESTS>
```

#### Example Execution

```bash
bash docker_run_client_metrics.sh my_repo my_image metrics_output 100
```
- `my_repo`: Docker repository name.
- `my_image`: Docker image name.
- `metrics_output`: Directory to store metrics.
- `100`: Number of requests each client should send.

This script automates the deployment and execution of multiple Docker containers to collect performance metrics from different servers, ensuring that each server configuration is validated and avoiding conflicts with duplicate IP/port combinations. The use of background processes and monitoring ensures that the script can handle multiple client instances efficiently.