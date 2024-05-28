#!/bin/bash

# URLs for the downloads
MODEL_URL="https://upatrasgr-my.sharepoint.com/:x:/g/personal/up1053647_upatras_gr/EY9I--dcctlKi1w9QBWUoPcBNS8-vjOOvoHspVXUHFr7iA?download=1"
DATASET_URL="https://upatrasgr-my.sharepoint.com/:x:/g/personal/up1053647_upatras_gr/EXyJVck4oONLnO9YPTIG8zgB2e8p0qd2coQhbyQti1x86g?download=1"
CLIENT_DATASET_URL="https://upatrasgr-my.sharepoint.com/:x:/g/personal/up1053647_upatras_gr/Ebr9rnpPhoJNlG8FULJOubcBelzHpTvM-NMm0SkNEtYD7w?download=1"

# Function to log progress
log_progress() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# Function to download and unzip the model
download_model() {
    log_progress "Creating directory ./Converter/models if it doesn't exist."
    mkdir -p ./Converter/models

    log_progress "Downloading model.zip."
    if ! wget --content-disposition -O ./Converter/models/model.zip "$MODEL_URL"; then
        log_progress "Error downloading model.zip."
        return 1
    fi

    log_progress "Unzipping model.zip to ./Converter/models."
    if ! unzip -o ./Converter/models/model.zip -d ./Converter/models; then
        log_progress "Error unzipping model.zip."
        return 1
    fi

    log_progress "Removing model.zip."
    rm ./Converter/models/model.zip
}

# Function to download and unzip the dataset
download_dataset() {
    log_progress "Creating directory ./Converter/datasets if it doesn't exist."
    mkdir -p ./Converter/datasets

    log_progress "Downloading dataset.zip."
    if ! wget --content-disposition -O ./Converter/datasets/dataset.zip "$DATASET_URL"; then
        log_progress "Error downloading dataset.zip."
        return 1
    fi

    log_progress "Unzipping dataset.zip to ./Converter/datasets."
    if ! unzip -o ./Converter/datasets/dataset.zip -d ./Converter/datasets; then
        log_progress "Error unzipping dataset.zip."
        return 1
    fi

    log_progress "Removing dataset.zip."
    rm ./Converter/datasets/dataset.zip
}

# Function to download the client dataset
download_client_dataset() {
    log_progress "Creating directory ./Composer/Client if it doesn't exist."
    mkdir -p ./Composer/Client

    log_progress "Downloading client_dataset."
    if ! wget --content-disposition -P ./Composer/Client "$CLIENT_DATASET_URL"; then
        log_progress "Error downloading client_dataset."
        return 1
    fi
}

# Main script execution
main() {
    log_progress "Starting download processes."

    download_model || log_progress "Model download process failed."

    download_dataset || log_progress "Dataset download process failed."

    download_client_dataset || log_progress "Client dataset download process failed."

    log_progress "All tasks completed."
}

# Run the main function
main
