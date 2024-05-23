#!/bin/bash

NAME=Client

# Record the start time (in seconds and nanoseconds)
start_time=$(date +%s%N)

# Check if the script receives exactly three arguments
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <absolute_input_path> <run_converter> <run_composer> <SRC_DIR> <input_framework>"
    exit 1
fi

absolute_input_path=$1
run_converter=$2
run_composer=$3
SRC_DIR=$4
input_framework=$5

# Ensure the logs directory exists
mkdir -p "${absolute_input_path}"/logs

# Then, direct the output to the file in the logs directory
exec > >(tee -ai "${absolute_input_path}"/logs/TF2AIF_run_${NAME,,}.log)
exec 2>&1

# Print the current date and time
echo "TF2AIF_run_${NAME,,}.sh script started on: $(date +"%Y-%m-%d %H:%M:%S")"

# Run Composer
if [ "$run_composer" = "True" ]; then
    SRC_COMPOSER_DIR=${SRC_DIR}/Composer
    composer_path=$absolute_input_path/Composer
    echo "Started Composer for ${NAME}"
    # If the directory doesn't exist, print a message and dont run Composer
    if [ ! -d "${composer_path}/${NAME}" ]; then
        echo "Directory ${composer_path}/${NAME} does not exist."
        echo "Composer for ${NAME} will not run" 
    else
        bash "${SRC_COMPOSER_DIR}"/${NAME}/composer_${NAME,,}.sh "${composer_path}" "${SRC_COMPOSER_DIR}"
        echo "bash ${SRC_COMPOSER_DIR}/${NAME}/composer_${NAME,,}.sh ${composer_path} ${SRC_COMPOSER_DIR}"
        echo "Composer for ${NAME} ended"
    fi
fi

end_time=$(date +%s%N)
# Calculate the elapsed time in seconds with milliseconds
elapsed_time=$(echo "scale=3; ($end_time - $start_time) / 1000000000" | bc)
echo "TF2AIF_run_${NAME,,} execution time: $elapsed_time seconds"