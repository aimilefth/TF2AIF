#!/bin/bash

NAME=ALVEO

# Record the Composer start time
start_time=$(date +%s%N)

# Check if the script receives exactly one argument
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <composer_path> <SRC_COMPOSER_DIR>"
    exit 1
fi

composer_path=$1
# SRC_COMPOSER_DIR is SRC_DIR from stable_v3
SRC_COMPOSER_DIR=$2
# Ensure the logs directory exists
mkdir -p "${composer_path}"/logs/

# Then, direct the output to the file in the logs directory
exec > >(tee -ai "${composer_path}"/logs/composer_${NAME,,}.log)
exec 2>&1

# Print the current date and time
echo "Composer script started on: $(date +"%Y-%m-%d %H:%M:%S")"

# Move to the input_path/AIF_container_creator/${NAME} dir
cd "${composer_path}/${NAME}" || { echo "composer_${NAME,,}.sh Failure to cd ${composer_path}/${NAME}"; exit 1; }

# List of files to check
files=(
  "${SRC_COMPOSER_DIR}/flask_server.py"
  "${SRC_COMPOSER_DIR}/utils.py"
  "${SRC_COMPOSER_DIR}/base_server.py"
  "${SRC_COMPOSER_DIR}/logconfig.ini"
  "${SRC_COMPOSER_DIR}/${NAME}/${NAME,,}_server.py"
  "${SRC_COMPOSER_DIR}/${NAME}/my_server.py"
  "../experiment_server.py"
  "../.env"
  "../composer_args.yaml"
  "../dockerhub_config.yaml"
  "composer_args_${NAME,,}.yaml"
  "extra_pip_libraries_${NAME,,}.txt"
  "${SRC_COMPOSER_DIR}/${NAME}/Dockerfile.${NAME,,}"
)

missing_files=()

# Check each file
for file in "${files[@]}"; do
  if [[ ! -f "$file" ]]; then
    missing_files+=("$file")
  fi
done

# If there are missing files, print them and exit
if [[ ${#missing_files[@]} -ne 0 ]]; then
  echo "The following required files are missing:"
  for missing in "${missing_files[@]}"; do
    echo "$missing"
  done
  exit 1
fi

# Check for at least one .xmodel file in the current directory
xmodel_files=$(find . -name "*.xmodel" -type f)
if [[ -z "$xmodel_files" ]]; then
  echo "No .xmodel files found."
  exit 1
fi

# List of variables to check
variables=(
  "REPO"
  "LABEL"
  "APP_NAME_ARG"
  "NETWORK_NAME_ARG"
  "NETWORK_TYPE_ARG"
  "FOCUS_ARG"
  "SERVER_MODE_ARG"
  "SERVER_IP_ARG"
  "SERVER_PORT_ARG"
  "MODEL_NAME_ARG"
  "BATCH_SIZE_ARG"
  "DEVICE_ARG"
  "CHANNELS_FIRST_ARG"
)

missing_variables=()

# Get argument values
while IFS=": " read -r key value; do
    # Remove any leading spaces on the value
    value=${value#"${value%%[![:space:]]*}"}
    # Export the key and value
    export "$key"="$value"
done < ../dockerhub_config.yaml

while IFS=": " read -r key value; do
    # Remove any leading spaces on the value
    value=${value#"${value%%[![:space:]]*}"}
    # Add the argument to the build args
    build_args="$build_args --build-arg $key=$value"
    export "$key"="$value"
done < ../composer_args.yaml

while IFS=": " read -r key value; do
    # Remove any leading spaces on the value
    value=${value#"${value%%[![:space:]]*}"}
    # Add the argument to the build args
    build_args="$build_args --build-arg $key=$value"
    export "$key"="$value"
done < composer_args_${NAME,,}.yaml

# Check each variable
for var in "${variables[@]}"; do
  if [[ -z "${!var}" ]]; then
    missing_variables+=("$var")
  fi
done

# If there are any missing variables, print them and exit
if [[ ${#missing_variables[@]} -ne 0 ]]; then
  echo "The following required variables are not set:"
  for missing in "${missing_variables[@]}"; do
    echo "$missing"
  done
  exit 1
fi

# Print REPO and LABEL for debugging
echo "REPO: $REPO"
echo "LABEL: $LABEL"

echo "$build_args"
# Copy files to current directory
cp -r "${SRC_COMPOSER_DIR}"/flask_server.py "${SRC_COMPOSER_DIR}"/utils.py "${SRC_COMPOSER_DIR}"/base_server.py "${SRC_COMPOSER_DIR}"/logconfig.ini "${SRC_COMPOSER_DIR}"/${NAME}/${NAME,,}_server.py "${SRC_COMPOSER_DIR}"/${NAME}/my_server.py ../experiment_server.py ../.env  ../extra_files_dir .

docker buildx build -f ${SRC_COMPOSER_DIR}/${NAME}/Dockerfile.${NAME,,} --platform linux/amd64 $build_args --tag ${REPO}:${LABEL}_${NAME,,} --push .
status=$?
if [ $status -eq 0 ]; then
    echo "Created Image at ${REPO}:${LABEL}_${NAME,,}"
else
    echo "Docker build failed with status: $status"
fi

# Remove files
rm -r flask_server.py utils.py base_server.py logconfig.ini ${NAME,,}_server.py my_server.py experiment_server.py .env extra_files_dir


end_time=$(date +%s%N)
# Calculate the elapsed time in seconds with milliseconds
elapsed_time=$(echo "scale=3; ($end_time - $start_time) / 1000000000" | bc)
echo "Composer ${NAME} execution time: $elapsed_time seconds"
