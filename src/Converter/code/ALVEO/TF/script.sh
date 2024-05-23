#!/bin/bash
# Setting up the environment
. /opt/vitis_ai/conda/etc/profile.d/conda.sh
conda activate base
export PATH=/opt/vitis_ai/conda/bin:$PATH
export VERSION=`cat /etc/VERSION.txt`
export BUILD_DATE=`cat /etc/BUILD_DATE.txt`
export VAI_ROOT=$VAI_ROOT
export VAI_HOME=$VAI_HOME
export PYTHONPATH=$PYTHONPATH
export XILINX_XRT=/opt/xilinx/xrt
export CUDA_HOME=/usr/local/cuda
export INTERNAL_BUILD=1
export LIBRARY_PATH=/usr/local/lib
export LD_LIBRARY_PATH=/opt/xilinx/xrt/lib:/usr/lib:/usr/lib/x86_64-linux-gnu:/usr/local/lib:/opt/vitis_ai/conda/envs/vitis-ai-tensorflow/lib
if [ -f /tmp/.Xauthority ]; then
    cp /tmp/.Xauthority ~/
    chmod -R 600 ~/.Xauthority
    sudo chown vitis-ai-user:vitis-ai-group ~/.Xauthority
fi
conda activate vitis-ai-tensorflow2 

python3 ${CONVERTER_APP}
