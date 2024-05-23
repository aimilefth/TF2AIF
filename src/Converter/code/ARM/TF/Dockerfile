FROM intel/intel-optimized-tensorflow:tf2.11.0-ubuntu-22.04

# Necessary for build
RUN apt-get update && apt-get install --no-install-recommends -y ffmpeg=7:4.4.2-0ubuntu0.22.04.1 libsm6=2:1.2.3-1build2 libxext6=2:1.3.4-1build1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Arguments
ARG CONVERTER_APP_ARG=converter.py
ARG LOG_CONFIG_ARG=logconfig.ini
ARG SCRIPT_ARG=script.sh
ARG DEVICE_ARG=ARM

ARG MODELS_PATH_ARG=/models
ARG LOGS_PATH_ARG=/logs/${DEVICE_ARG}
ARG OUTPUTS_PATH_ARG=/outputs/${DEVICE_ARG}
ARG DATASETS_PATH_ARG=/datasets
ARG DATALOADERS_PATH_ARG=/dataloaders

# Environmental Variables
ENV CONVERTER_APP=${CONVERTER_APP_ARG}
ENV LOG_CONFIG=${LOG_CONFIG_ARG}
ENV SCRIPT=${SCRIPT_ARG}
ENV LOG_FILE=${LOGS_PATH_ARG}/Converter_${DEVICE_ARG}
ENV MODELS_PATH=${MODELS_PATH_ARG}
ENV LOGS_PATH=${LOGS_PATH_ARG}
ENV OUTPUTS_PATH=${OUTPUTS_PATH_ARG}
ENV DATASETS_PATH=${DATASETS_PATH_ARG}
ENV DATALOADERS_PATH=${DATALOADERS_PATH_ARG}

ENV MODEL_NAME=default_model
ENV DATASET_NAME=default_dataset
ENV TRAINED=False
ENV DATALOADER_NAME=default_dataloader.py

ENV QUANTIZATION_SAMPLES=50

# Copy Files
COPY ${CONVERTER_APP_ARG} ${WORKING_DIR_ARG}
COPY ${LOG_CONFIG_ARG} ${WORKING_DIR_ARG}
COPY ${SCRIPT_ARG} ${WORKING_DIR_ARG}

CMD /bin/bash ${SCRIPT}