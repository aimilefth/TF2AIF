# AGX Docker Image

This directory contains the Dockerfile and build script to create a Docker image optimized for executing model inference using the [ONNX Runtime framework](https://onnxruntime.ai/) on the Nvidia Jetson AGX platform.  It installs necessary system dependencies and Python libraries, including support for [ONNX](https://onnx.ai/).

## Base Image

The Docker image for the AGX platform is based on the [Nvidia L4T TensorFlow Docker](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-tensorflow) images.

## Constraints

This image is tested on [Nvidia Jetson Xavier Series](https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-xavier-series/) devices that contain [Jetpack 4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461) [L4T 32.7.1] or [Jetpack 4.6.3](https://developer.nvidia.com/jetpack-sdk-463) [L4T 32.7.3]. It should work for other Nvidia Jetson Devices, given they contain Jetpack 4.6.x . For other Jetpack versions, the base image version needs to change according to the [Nvidia L4T TensorFlow Docker catalog](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-tensorflow).

## Useful resources

[Nvidia L4T Tensorflow](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/l4t-tensorflow)
[Jetson Zoo wiki](https://elinux.org/Jetson_Zoo)
[Jetson Zoo wiki, ONNX Runtime](https://elinux.org/Jetson_Zoo#ONNX_Runtime)
[jetson-containers github repo](https://github.com/dusty-nv/jetson-containers)