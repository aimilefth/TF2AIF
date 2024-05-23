#!/bin/bash

NAME=ARM

# Record the Converter start time
start_time=$(date +%s%N)

# Check if the script receives exactly one argument
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <converter_path> <input_framework>"
    exit 1
fi

# Get the converter_path
converter_path=$1
input_framework=$2

# Ensure the logs and outputs directories exist
mkdir -p "${converter_path}/logs/${NAME}"
mkdir -p "${converter_path}/outputs/${NAME}"

# Then, Direct the output to the file in the logs directory
exec > >(tee -ai "${converter_path}"/logs/converter_${NAME,,}.log)
exec 2>&1

echo "Converter script started on: $(date +"%Y-%m-%d %H:%M:%S")"

converter_configs_path=${converter_path}/configurations
cd "${converter_configs_path}" || { echo "converter_${NAME,,}.sh Failure to cd ${converter_configs_path}"; exit 1; }


yaml_files=(
  "${NAME}/converter_args_${NAME,,}.yaml"
  "converter_args.yaml"
)
yaml_missing_files=()

# Check each file
for file in "${yaml_files[@]}"; do
  if [[ ! -e "$file" ]]; then
    yaml_missing_files+=("$file")
  fi
done

# If there are missing yaml files print them and exit
if [[ ${#yaml_missing_files[@]} -ne 0 ]]; then
  echo "The following required files are missing:"
  for missing in "${yaml_missing_files[@]}"; do
    echo "$missing"
  done
  exit 1
fi

# Get argument values
while IFS=": " read -r key value; do
    # Remove any leading spaces on the value
    value=${value#"${value%%[![:space:]]*}"}
    # Export the key and value
    export $key=$value
    # Print the key and value
    echo "$key: $value"
done < ./${NAME}/converter_args_${NAME,,}.yaml

# Get argument values
while IFS=": " read -r key value; do
    # Remove any leading spaces on the value
    value=${value#"${value%%[![:space:]]*}"}
    # Export the key and value
    export $key=$value
    # Print the key and value
    echo "$key: $value"
done < ./converter_args.yaml

# Get correct IMAGE_NAME
IMAGE_NAME=${IMAGE_NAME}:${input_framework,,}_${NAME,,}

# Get absolute Paths (needed for docker run)
MODELS_PATH=/$(pwd)/${MODELS_PATH}
LOGS_PATH=/$(pwd)/${LOGS_PATH}
DATASETS_PATH=/$(pwd)/${DATASETS_PATH}
OUTPUTS_PATH=/$(pwd)/${OUTPUTS_PATH}
DATALOADERS_PATH=/$(pwd)/${DATALOADERS_PATH}

directories=(
  "$MODELS_PATH"
  "$LOGS_PATH"
  "$DATASETS_PATH"
  "$OUTPUTS_PATH"
  "$DATALOADERS_PATH"
)

if [[ "$input_framework" == "TF" ]]; then 
  files=(
    "${MODELS_PATH}/${MODEL_NAME}"
    "${DATASETS_PATH}/${DATASET_NAME}"
    "${DATALOADERS_PATH}/${DATALOADER_NAME}"
  )

  # List of variables to check
  variables=(
    "TRAINED"
  )
elif [[ "$input_framework" == "PT" ]]; then 
  files=(
    "${MODELS_PATH}/${MODEL_NAME}"
    "${DATASETS_PATH}/${DATASET_NAME}"
    "${DATALOADERS_PATH}/${DATALOADER_NAME}"
    "${MODELS_PATH}/${MODEL_CLASS_FILE}"
  )

  # List of variables to check
  variables=(
    "TRAINED"
    "MODEL_CLASS_NAME"
    "INPUT_SHAPE"
  )
fi

missing_files=()
missing_directories=()
missing_variables=()

# Check each directory
for dir in "${directories[@]}"; do
  if [[ ! -d "$dir" ]]; then
    missing_directories+=("$dir")
  fi
done

# Check each file
for file in "${files[@]}"; do
  if [[ ! -e "$file" ]]; then
    missing_files+=("$file")
  fi
done

# Check each variable
for var in "${variables[@]}"; do
  if [[ -z "${!var}" ]]; then
    missing_variables+=("$var")
  fi
done

# If there are missing directories, files, or variables, print them and exit
if [[ ${#missing_directories[@]} -ne 0 ]] || [[ ${#missing_files[@]} -ne 0 ]] || [[ ${#missing_variables[@]} -ne 0 ]]; then
  if [[ ${#missing_directories[@]} -ne 0 ]]; then
    echo "The following required directories are missing:"
    for missing in "${missing_directories[@]}"; do
      echo "$missing"
    done
  fi

  if [[ ${#missing_files[@]} -ne 0 ]]; then
    echo "The following required files are missing:"
    for missing in "${missing_files[@]}"; do
      echo "$missing"
    done
  fi

  if [[ ${#missing_variables[@]} -ne 0 ]]; then
    echo "The following required variables are not set:"
    for missing in "${missing_variables[@]}"; do
      echo "$missing"
    done
  fi
  
  exit 1
fi

USER_ID=$(id -u)
GROUP_ID=$(id -g)

if [[ "$input_framework" == "TF" ]]; then 
docker_run_params=$(cat <<-END
    -u ${USER_ID}:${GROUP_ID} \
    -v ${MODELS_PATH}:/models \
    -v ${LOGS_PATH}:/logs \
    -v ${DATASETS_PATH}:/datasets \
    -v ${OUTPUTS_PATH}:/outputs \
    -v ${DATALOADERS_PATH}:/dataloaders \
    --env MODEL_NAME=${MODEL_NAME} \
    --env TRAINED=${TRAINED} \
    --env DATASET_NAME=${DATASET_NAME} \
    --env DATALOADER_NAME=${DATALOADER_NAME} \
    --pull=always \
    --rm \
    --network=host \
    --name=converter_${input_framework,,}_${NAME,,}_${MODEL_NAME} \
    ${IMAGE_NAME}
END
)
elif [[ "$input_framework" == "PT" ]]; then 
docker_run_params=$(cat <<-END
    -u ${USER_ID}:${GROUP_ID} \
    -v ${MODELS_PATH}:/models \
    -v ${LOGS_PATH}:/logs \
    -v ${DATASETS_PATH}:/datasets \
    -v ${OUTPUTS_PATH}:/outputs \
    -v ${DATALOADERS_PATH}:/dataloaders \
    --env MODEL_NAME=${MODEL_NAME} \
    --env TRAINED=${TRAINED} \
    --env DATASET_NAME=${DATASET_NAME} \
    --env DATALOADER_NAME=${DATALOADER_NAME} \
    --env MODEL_CLASS_FILE=${MODEL_CLASS_FILE} \
    --env MODEL_CLASS_NAME=${MODEL_CLASS_NAME} \
    --env INPUT_SHAPE=${INPUT_SHAPE} \
    --pull=always \
    --rm \
    --network=host \
    --name=converter_${input_framework,,}_${NAME,,}_${MODEL_NAME} \
    ${IMAGE_NAME}
END
)
fi

docker run \
  $docker_run_params

end_time=$(date +%s%N)
# Calculate the elapsed time in seconds with milliseconds
elapsed_time=$(echo "scale=3; ($end_time - $start_time) / 1000000000" | bc)
echo "Converter ${NAME} execution time: $elapsed_time seconds"
