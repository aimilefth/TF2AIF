#!/usr/bin/env bash
# Copyright 2021 Xilinx Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [[ "$CONDA_DEFAULT_ENV" = "base" ]]; then
  echo "WARNING: No conda environment has been activated."
fi

if [[ -z $VAI_HOME ]]; then
	export VAI_HOME="$( readlink -f "$( dirname "${BASH_SOURCE[0]}" )/../.." )"
fi

echo "------------------"
echo "VAI_HOME = $VAI_HOME"
echo "------------------"

source /opt/xilinx/xrt/setup.sh
echo "---------------------"
echo "XILINX_XRT = $XILINX_XRT"
echo "---------------------"

source /opt/xilinx/xrm/setup.sh
echo "---------------------"
echo "XILINX_XRM = $XILINX_XRM"
echo "---------------------"

echo "---------------------"
echo "LD_LIBRARY_PATH = $LD_LIBRARY_PATH"
echo "---------------------"

case $1 in

  U200)
    export XCLBIN_PATH=/opt/xilinx/overlaybins/dpuv3int8
    export XLNX_VART_FIRMWARE=/opt/xilinx/overlaybins/dpuv3int8/dpdpuv3_wrapper.hw.xilinx_u200_gen3x16_xdma_1_202110_1.xclbin
    ;;
  
  U50_L)
    export XCLBIN_PATH=/opt/xilinx/overlaybins/dpuv3me
    export XLNX_VART_FIRMWARE=/opt/xilinx/overlaybins/dpuv3me/dpuv3me_1E333_xilinx_u50_gen3x4_xdma_base_2.xclbin
    ;;

  U280_L)
    export XCLBIN_PATH=/opt/xilinx/overlaybins/dpuv3me
    export XLNX_VART_FIRMWARE=/opt/xilinx/overlaybins/dpuv3me/dpuv3me_2E250_xilinx_u280_xdma_201920_3.xclbin
    ;;
  
  U50_H)
    export XCLBIN_PATH=/opt/xilinx/overlaybins/dpuv3e
    export XLNX_VART_FIRMWARE=/opt/xilinx/overlaybins/dpuv3e/dpuv3e_6E300_xilinx_u50_gen3x4_xdma_base_2.xclbin
    ;;

  U280_H)
    export XCLBIN_PATH=/opt/xilinx/overlaybins/dpuv3e
    export XLNX_VART_FIRMWARE=/opt/xilinx/overlaybins/dpuv3e/dpuv3e_14E300_xilinx_u280_xdma_201920_3.xclbin
    ;;

  *)
    echo "Invalid argument $1!!!!"
    ;;
esac


echo "---------------------"
echo "XCLBIN_PATH = $XCLBIN_PATH"
echo "XLNX_VART_FIRMWARE = $XLNX_VART_FIRMWARE"
echo "---------------------"
