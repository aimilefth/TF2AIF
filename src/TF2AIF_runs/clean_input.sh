#!/bin/bash

# This script cleans up specified directories and optionally removes model-related files within the given input path.
#
# Usage: ./clean_input.sh <input_path> [clean_models]
#
# Arguments:
#   input_path: The base directory where the logs and other specified directories are located.
#   clean_models: (Optional) If set to "True", the script will also clean model directories while preserving certain files. Defaults to "False".
#
# Functionality:
# 1. Checks if at least one argument (input_path) is provided; if not, it prints the usage and exits.
# 2. Sets the input_path from the first argument and clean_models flag from the second argument (if provided).
# 3. Defines an array of directories that contain the logs and the Converter outputs, removing each if it exists.
# 4. If clean_models is set to "True", iterates over the list of AI-framework/platform pair directories, preserving the Composer configuration files while removing the rest, such as the framework-specific model created by the Converter.
# 5. Prints the progress and results of the directory removal process.
#
# The script helps in resetting the environment by removing logs, outputs, and other temporary files generated during the TF2AIF run, making it easier to prepare for new runs.

# Default value for clean_models
clean_models="False"

# Check if an input path is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <input_path> [clean_models]"
    exit 1
fi

# Assign the input path
input_path="$1"

# Check for second argument and update clean_models accordingly
if [ "$#" -ge 2 ]; then
    clean_models="$2"
fi

# Define the directories to be removed
directories=(
    "${input_path}/logs"
    "${input_path}/Converter/logs"
    "${input_path}/Converter/outputs"
    "${input_path}/Composer/logs"
)

# Iterate over the array and remove each directory if it exists
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "Removing directory: $dir"
        rm -rf "$dir"
    else
        echo "Directory not found: $dir"
    fi
done

dirs=("AGX" "ALVEO" "ARM" "CPU" "GPU" "AGX_TF" "ARM_TF" "CPU_TF" "GPU_TF")

if [ "$clean_models" = "True" ]; then
    for dir in "${dirs[@]}"; do
        keep_files=(
            "composer_args_${dir,,}.yaml"
            "extra_pip_libraries_${dir,,}.txt"
            "Readme_${dir,,}.txt"
        )
        dir_to_check="${input_path}/Composer/${dir}"
        
        # Check if the directory exists before cleaning
        if [ -d "$dir_to_check" ]; then
            # Remove files/directories not listed in keep_files
            for item in "${dir_to_check}"/*; do
                item_base=$(basename "$item")
                keep=false
                for keep_file in "${keep_files[@]}"; do
                    if [[ "$item_base" == "$keep_file" ]]; then
                        keep=true
                        break
                    fi
                done
                if [ "$keep" = false ]; then
                    echo "From directory ${dir}, removing item: $item"
                    rm -rf "$item"
                fi
            done
        fi 
    done
fi

echo "Directory removal process completed."

