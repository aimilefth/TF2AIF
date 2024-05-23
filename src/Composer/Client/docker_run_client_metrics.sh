#!/bin/bash

REPO_NAME=$1
IMAGE_NAME=$2
METRICS_DIR=$3
NUMBER_OF_REQUESTS=$4

# Single array holding the directory, IP, and port
data=("AGX" "192.168.1.250" "3000"
      "ALVEO" "192.168.1.228" "3001"
      "ARM" "192.168.1.250" "3001"
      "CPU" "192.168.1.228" "3000"
      "GPU" "192.168.1.229" "3000"
      "GPU_GENERIC" "192.168.1.229" "3001"
     )

echo ${REPO_NAME}
# IP/PORT CHECKING
function is_valid_ip() {
    local ip=$1
    local valid_ip_regex="^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    [[ $ip =~ $valid_ip_regex ]]
}

function is_valid_port() {
    local port=$1
    [[ "$port" =~ ^[0-9]+$ ]] && [ "$port" -ge 1 ] && [ "$port" -le 65535 ]
}

declare -A used_combinations

# Validate IPs, Ports and check for duplicates
for ((i=0; i<${#data[@]}; i+=3)); do
    dir=${data[i]}
    current_ip=${data[i+1]}
    current_port=${data[i+2]}
    
    # Validate IP and Port format
    if ! is_valid_ip "$current_ip"; then
        echo "Invalid IP format for directory $dir: $current_ip"
        exit 1
    fi
    
    if ! is_valid_port "$current_port"; then
        echo "Invalid port format for directory $dir: $current_port"
        exit 1
    fi
    
    # Check for duplicate IP/Port combinations
    if [[ ${used_combinations["$current_ip:$current_port"]} ]]; then
        echo "Duplicate IP/Port combination detected for directory $dir: $current_ip:$current_port"
        exit 1
    fi
    used_combinations["$current_ip:$current_port"]=1
done

# MAIN WORK
# Declare an associative array to hold the PIDs of the child processes and their corresponding directory names
declare -A pids

# Iterate over the array in steps of 3 (dir, IP, port)
for ((i=0; i<${#data[@]}; i+=3)); do
    dir=${data[i]}
    current_ip=${data[i+1]}
    current_port=${data[i+2]}
    # Run the child script in the background
    setsid docker run --rm --name ${METRICS_DIR}_client_${dir,,} --network=host --pull=always --env NUMBER_OF_REQUESTS=${NUMBER_OF_REQUESTS} --env SERVER_IP=${current_ip} --env SERVER_PORT=${current_port} -v /$(pwd)/${METRICS_DIR}:/home/Documents/mounted_dir ${REPO_NAME}:${IMAGE_NAME}_client python3 metrics_script.py >/dev/null 2>&1 < /dev/null &
    # Add the PID of the child process to the array with its corresponding directory name
    pids[$!]="$dir"
    echo "Running ${METRICS_DIR}_client_${dir,,} with SERVER_IP ${current_ip} and SERVER_PORT ${current_port}"
done

# WAITING PROCESSES
# While there are still processes running
while ((${#pids[@]})); do
    # For each PID in the list
    for pid in "${!pids[@]}"; do
        # If the process has finished
        if ! kill -0 $pid 2>/dev/null; then
            # Print a message with the directory name instead of the PID
            echo "Process for ${METRICS_DIR}_client_${pids[$pid],,}  finished."
            # Remove the PID from the list
            unset pids[$pid]
        fi
    done
    # Sleep for a while to avoid excessive CPU usage
    sleep 1
done