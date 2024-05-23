Aimilios Leftheriotis
Achilleas Tzenetopoulos
Microlab@NTUA

AI@EDGE project


EXPERIMENT-specific files to change
1) dockerhub_config.yaml: Choose image name and label

SERVER-SPECIFIC files to change
1) my_client.py: Platform-specific server code
2) docker_build_args_client.yaml: Platform-specific docker build arguments
3) Add your dataset

=========================
DOCKER BUILD INSTRUCTIONS
=========================
To build the Docker image for the client, execute the following command:

#docker buildx build -f ./Dockerfile.client --platform linux/amd64,linux/arm64 --tag aimilefth/tf2aif_exp_v2:class_thr_client --push .
bash ../../../src/AIF_container_creator/docker_build_client.sh
(Run it from this directory)

The resulting image name is configured by the ../docker_hub_config.yaml file

for example docker_hub_config.yaml

REPO: aimilefth/tf2aif_exp_v2
LABEL: class_thr

the image will be ${REPO}:${LABEL}_client, meaning
aimilefth/tf2aif_exp_v2:class_thr_client

==============
DOCKER RUN CMD
==============
To run the Docker container on the host, execute the following command:

docker run -it --rm --name client --network=host --pull=always aimilefth/tf2aif_exp_v2:class_thr_client

====================================
EXECUTE ON CONTAINER TO GET INFERENCE
====================================


To execute on the container and get inference, execute the following command:

python3 ${CLIENT_APP} 
or
python3 client.py

========================================================
EXECUTE ON CONTAINER TO GET METRICS IN JSON FORMAT
========================================================
To execute on the container and get metrics in JSON format, execute the following command:

python3 ${CLIENT_APP} -m True

===============================
ENVIRONMENT VARIABLES
===============================
The following environment variables can be set to manage the client:

SERVER_IP: The IP address of the server
SERVER_PORT: The port of the server
