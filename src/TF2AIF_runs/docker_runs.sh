#!/bin/bash

# Default values
image_name=""
image_app=""
device=""
yaml_file=""
gpu_device_number="0"  # Default GPU device number
supported_devices="AGX ALVEO ARM CLIENT CPU GPU AGX_TF ARM_TF CPU_TF GPU_TF"
# Help message for usage
usage() {
    echo "Usage: $0 -n <image_name> -a <image_app> -d <device> [-y <yaml_file>]"
    echo "Devices: $(echo $supported_devices | tr ' ' ', ')"
    exit 1
}

# Process command-line options
while getopts "n:a:d:y:" opt; do
  case $opt in
    n) image_name="$OPTARG" ;;
    a) image_app="$OPTARG" ;;
    d) device="$OPTARG" ;;
    y) yaml_file="$OPTARG" ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage ;;
  esac
done

# Validate inputs
if [[ -z "$image_name" || -z "$image_app" || -z "$device" ]]; then
    echo "Options -n, -a, and -d must be provided."
    usage
fi

# Normalize device input to uppercase for comparison
device_upper_case=$(echo "$device" | tr '[:lower:]' '[:upper:]')
device_lower_case=${device_upper_case,,}

# Check if the device type is supported
if [[ ! " $supported_devices " =~ " $device_upper_case " ]]; then
    echo "Error: Unsupported device type '$device'."
    usage
fi

# Construct the image tag
IMAGE="${image_name}:${image_app}_${device_lower_case}"

# Check if the Docker image can be pulled
if ! docker pull "$IMAGE"; then
    echo "Error: Image '$IMAGE' cannot be pulled from the remote repository."
    exit 1
fi

env_vars=""
if [[ -n "$yaml_file" ]]; then
    # Check if the YAML file exists
    if [ ! -f "$yaml_file" ]; then
        echo "Error: YAML file '$yaml_file' not found."
        exit 1
    fi

    # Read and parse the YAML file into Docker environment variables
    echo "YAML Environment Variables:"
    while IFS=": " read -r key value; do
        value=${value#"${value%%[![:space:]]*}"} # Remove leading spaces
        if [[ "$key" == "GPU_DEVICE_NUMBER" ]]; then
            gpu_device_number="$value"
        else
            env_vars+="--env $key='$value' "
        fi
        export "$key"="$value"
        echo "$key=$value"
    done < "$yaml_file"
fi

# Prepare the Docker run command based on the device type
docker_run_command="docker run -it --rm --network=host --pull=always $env_vars -v /scrape:/scrape "

case "$device_upper_case" in
    AGX|AGX_TF|AGX_PT)
        docker_run_command+="--runtime nvidia "
        ;;
    GPU|GPU_TF|GPU_PT|GPU_TFTRT)
        docker_run_command+="--gpus device=$gpu_device_number "
        ;;
    ALVEO)
        # Special handling for ALVEO devices
        xclmgmt_driver="$(find /dev -name xclmgmt\*)"
        render_driver="$(find /dev/dri -name renderD\*)"
        for i in ${xclmgmt_driver} ${render_driver}; do
            docker_run_command+="--device=$i "
        done
        docker_run_command+="-v /dev/shm:/dev/shm -v /opt/xilinx/dsa:/opt/xilinx/dsa -v /opt/xilinx/overlaybins:/opt/xilinx/overlaybins -v /etc/xbutler:/etc/xbutler "
        ;;
    VERSAL|ZYNQ)
        docker_run_command+="--privileged -v /run/media:/run/media "
esac
docker_run_command+="--name ${image_app}_${device} $IMAGE"

# Display the complete Docker run command before executing it
echo "Complete Docker run command:"
echo "$docker_run_command"

# Execute the Docker command
eval "$docker_run_command"
