#!/bin/bash

# Function to update or add a YAML entry
update_yaml() {
    local yaml_file=$1
    local key=$2
    local value=$3

    if grep -q "^${key}:" "$yaml_file"; then
        sed -i "s/^${key}:.*$/${key}: ${value}/" "$yaml_file"
        echo "Updated ${key} in ${yaml_file} to ${value}"
    else
        # Ensure it adds a newline before appending if the file does not end with a newline
        sed -i -e '$a\' "$yaml_file"
        echo "${key}: ${value}" >> "$yaml_file"
        echo "Added ${key} to ${yaml_file}"
    fi
}

NAME=ARM_TF

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

# Move files from Converter to Composer and modify Composer Yamls
if [ "$run_converter" = "True" ] && [ "$run_composer" = "True" ]; then
    source_path=${absolute_input_path}/Converter/models
    destination_path=${absolute_input_path}/Composer/${NAME}
    # Move outputs to Composer folders
    # Arrays for extensions and corresponding YAML arguments
    declare -A ext_to_arg=(["directory"]="MODEL_NAME_ARG")
    declare -A moved_files
    # Read the YAML file line by line and extract the value of MODEL_NAME
    while IFS= read -r line; do
        if [[ $line == MODEL_NAME* ]]; then
            model_name="${line#*: }"
        fi
    done < "${absolute_input_path}/Converter/configurations/converter_args.yaml"
    echo "Model name to be copied is: ${model_name}"

    # Check if the model exists
    if [ -e "${source_path}/${model_name}" ]; then
        # Copy the model to the destination directory
        echo "Copying ${model_name} to ${destination_path}"
        cp -r "${source_path}/${model_name}" "${destination_path}"/
        moved_files["directory"]=${model_name}
    fi

    # Updating YAML files based on the extension to argument mapping
    for ext in "${!moved_files[@]}"; do
        # Check if the extension has an ARG for the yaml file
        if [[ -n "${ext_to_arg[$ext]}" ]]; then
            file_name=${moved_files[$ext]}
            yaml_key=${ext_to_arg[$ext]}
            yaml_file="${destination_path}/composer_args_${NAME,,}.yaml"  # Assuming a common YAML for simplicity
            if [[ -n $file_name ]]; then
                update_yaml "$yaml_file" "$yaml_key" "$file_name"
            else
                echo "No file name available, skipping YAML update."
            fi
        fi
    done
fi

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