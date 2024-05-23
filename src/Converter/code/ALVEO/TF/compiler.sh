#!/bin/bash

<<com
Aimilios Leftheriotis
Microlab@NTUA
VLSILab@UPatras

This script is part of the Converter tool used for AI@EDGE.
This code compiles a quantized Tensorflow2 model to a xmodel.
Need to make it executable.
com


# Use this to enable exit with | tee
start=`date +%s`

# https://www.baeldung.com/linux/use-command-line-arguments-in-bash-script

while getopts n:o:q:a:l: flag
do
    case "${flag}" in
        n) model_name=${OPTARG};;
        o) output_path=${OPTARG};;
        q) q_model_path_name=${OPTARG};;
        a) arch=${OPTARG};;
        l) log_file=${OPTARG};;
    esac
done

print_arguments(){
    echo "Model name: ${model_name}"
    echo "Output path: ${output_path}"
    echo "Quantized model path_name: ${q_model_path_name}"
    echo "Arch: ${arch}"
    echo "Log file: ${log_file}"
}

assert_arch(){
    valid_archs=(u280_l u280_h)
    if [[ ! " ${valid_archs[*]} " =~ " ${arch} " ]]
    then
        echo "Arch is not valid, got ${arch}"
        exit 1
    fi
}

print_arguments 2>&1 | tee -a ${log_file}
assert_arch 2>&1 | tee -a ${log_file}

get_ARCH(){
    if [ ${arch} == u280_l ]
    then
        export ARCH=/opt/vitis_ai/compiler/arch/DPUCAHX8L/U280/arch.json
        echo ${ARCH} 2>&1 | tee -a  ${log_file}
    elif [ ${arch} == u280_h ]
    then
        export ARCH=/opt/vitis_ai/compiler/arch/DPUCAHX8H/U280/arch.json
        echo ${ARCH} 2>&1 | tee -a  ${log_file}
    else
        echo "Arch passed assert_arch but not valid arch, got ${arch}"
        exit 1
    fi
}

# Cant export variables if i have tee
#get_ARCH 2>&1 | tee -a ${LOG_NAME}
get_ARCH

compile() {
      vai_c_tensorflow2 \
            --model           ${q_model_path_name} \
            --arch            ${ARCH} \
            --output_dir      ${output_path} \
            --net_name        ${model_name}_${arch}
}

compile 2>&1 | tee -a  ${log_file}

end=`date +%s`
runtime=$((end-start))
echo "Compile execution time ${runtime} s" 2>&1 | tee -a ${LOG_NAME}

