# Base container images

The Base container images directory provides a collection of Dockerfiles and build scripts to construct Docker images that can be used for AI-framework/platform combinations.

These images are optimized for different frameworks for platforms such as AGX, ALVEO, ARM, CPU, and GPU. There is also the implementation of images which can execute native TensorFlow, for each platform. Additionally, there is the simple Client base image. Each directory in the repository represents a specific AI-framework/platform combination and contains two main files:

1) `Dockerfile` - Contains all the instructions for Docker to build the image. This includes the base image to start from and the necessary dependencies.
2) `docker_build.sh` - A Bash script that can be executed to build and push the Docker image to the Docker registry. 

## Build Instructions 

All the images are already built and available in the [aimilefth/aate_container_templates DockerHub repository](https://hub.docker.com/repository/docker/aimilefth/aate_container_templates/general). However, if you need to rebuild any of the templates or add a new base container image, follow these instructions:

### Rebuilding a Base Container Image

1. **Navigate to the appropriate directory**:
   Each sub-directory contains its own `Dockerfile` and build script. To build and push a Docker image for a particular platform, navigate to the appropriate directory. For example:

```shell
cd AGX
```

2. **Modify the `docker_build.sh` script**:
    Change the docker image name inside the `docker_build.sh` script to reflect your custom image name. For example:

```bash
docker buildx build -f ./Dockerfile --platform linux/arm64 --tag your_dockerhub_username/custom_image_name:agx --push .
```

3. **Execute the build script**:
    Run the modified docker_build.sh script to build and push the Docker image to your Docker registry.

```shell
bash docker_build.sh
```

4. Update Dockerfiles used in Composer flow:
    If you change the name of the base container image, ensure that you update the names of the Dockerfiles used in the Composer flow to match your new base container images. For example, if you change the AGX base container image, update the FROM directive in the [Dockerfile.agx example](src/Composer/AGX/Dockerfile.agx) as follows:

```dockerfile
FROM your_dockerhub_username/custom_image_name:agx
```

### Building All Images

Alternatively, you can use the docker_build_all.sh script to build all the images for all platforms. Ensure you have updated the script to reflect your custom image names if necessary.

## Hardware Platforms

### AGX

The Docker image for the AGX platform is based on the Nvidia L4T TensorFlow Docker image. This image includes TensorFlow with support for Nvidia's AGX platform and support for the [ONNX Runtime framework](https://onnxruntime.ai/). More information on the AGX/README.md file.

### ALVEO

The Docker image for the Alveo platform is based on the Xilinx Vitis AI Docker image. This image includes [Vitis AI](https://github.com/Xilinx/Vitis-AI/tree/1.4.1) with support for Xilinx's Alveo FPGAs. More information on the ALVEO/README.md file.

### ARM

The Docker image for the ARM platform is based on the Arm Software Developer's TensorFlow Docker image. This image includes TensorFlow with support for ARM's Neoverse platform, enabling the [TensorFlow Lite framework](https://www.tensorflow.org/lite).

### Client

The Docker image for the Client side is based on the official Python Docker image. This image includes Python and essential libraries required for the client side.

### CPU

The Docker image for the CPU platform is based on the Intel-optimized TensorFlow Docker image. This image includes TensorFlow optimized for Intel CPUs, , enabling the [TensorFlow Lite framework](https://www.tensorflow.org/lite).

### GPU

The Docker image for the GPU platform is based on the official TensorFlow Docker image with GPU support. This image includes TensorFlow with GPU acceleration, with support for the [ONNX Runtime framework](https://onnxruntime.ai/).


### AGX_TF, ARM_TF, CPU_TF, GPU_TF

These Docker images enable running native TensorFlow on the appropriate platform.

## Docker Images

The Docker images built from these Dockerfiles are pushed to [this Docker registry](https://hub.docker.com/r/aimilefth/aate_container_templates) under the name aimilefth/aate_container_templates:<platform>, where <platform> is replaced with the name of the specific hardware platform (e.g., agx, alveo, etc).


## Tests

| Platform    | TF version  | PT version  | AI-Framework        | Device             | Tested |
|-------------|-------------|-------------|---------------------|--------------------|--------|
| AGX         | 2.7         | 1.7         | ONNX Runtime 1.11.0 | Jetson AGX Xavier  | Yes    |
| ALVEO       | 2.3         | 1.7         | Vitis-AI 1.4.1      | ALVEO U280         | Yes    |
| ARM         | 2.11        | 1.7         | TensorFlow Lite     | Any ARM Device     | Yes    |
| CPU         | 2.11        | 1.7         | TensorFlow Lite     | Any x86 Device     | Yes    |
| GPU         | 2.11        | 1.7         | ONNX Runtime 1.14.0 | Any Nvidia GPU     | Yes    |
| AGX_TF      | 2.7         | N/A         | TensorFlow          | Jetson AGX Xavier  | Yes    |
| ARM_TF      | 2.11        | N/A         | TensorFlow          | Any ARM Device     | Yes    |
| CPU_TF      | 2.11        | N/A         | TensorFlow          | Any x86 Device     | Yes    |
| GPU_TF      | 2.11        | N/A         | TensorFlow          | Any Nvidia GPU     | Yes    |
| Client      | N/A         | N/A         | N/A                 | Any x86/ARM Device | Yes    |


## More Information

More information on the individual README.md files on each subdirectory
#ALVEO TF version is not upgradable (stuck on Vitis-AI 2.3) \