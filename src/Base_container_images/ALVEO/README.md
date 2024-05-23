# ALVEO Docker Image

This directory contains the Dockerfile and build script to create a Docker image optimized for executing model inference using the [AMD Vitis AI framework](https://github.com/Xilinx/Vitis-AI) on the [AMD ALVEO](https://www.amd.com/en/products/accelerators/alveo.html) platform.  It installs necessary system dependencies and Python libraries.

## Base Image

The Docker image for the ALVEO platform is based on the [Vitis AI Docker images](https://hub.docker.com/r/xilinx/vitis-ai).

## Constraints

This image is tested on the [AMD Alveo U280](https://www.xilinx.com/products/boards-and-kits/alveo/u280.html) device, on a server containing Vitis AI 1.4.1, after following the [setup guide for Alveo U280](https://github.com/Xilinx/Vitis-AI/tree/v1.4.1/setup/alveo). In detail, XRT : 2.11.634 , XRM : 1.2.1539, Target Platform: fpga-xilinx_u280_xdma_201920_3-1579649056. It should work for other Vitis AI 1.4.1 supported Alveo devices, but the Converter and Composer code would require some changes. Upgrading to a higher Vitis AI version would require upgrading the Base Image.

## Useful resources

[Vitis-AI github repo](https://github.com/Xilinx/Vitis-AI/blob/v1.4.1)
[Vitis-AI User Guide](https://docs.amd.com/r/1.4.1-English/ug1414-vitis-ai/Vitis-AI-Overview)
[Vitis-AI Dockerhub](https://hub.docker.com/r/xilinx/vitis-ai)
[Vitis-AI Documentation](https://xilinx.github.io/Vitis-AI/3.5/html/index.html)