# CLASSIFICATION_THR Converter Flow

## Overview

The Input Directory for the Converter module contains the necessary configuration files, datasets, and models required to convert AI models to different formats for various AI-framework/platform pairs. Each AI-framework/platform combination has its specific configuration files to ensure optimal performance and compatibility during the conversion process.

## Directory Structure

```
.
├── configurations
│   ├── AGX
│   │   └── converter_args_agx.yaml
│   ├── ALVEO
│   │   └── converter_args_alveo.yaml
│   ├── ARM
│   │   └── converter_args_arm.yaml
│   ├── CPU
│   │   └── converter_args_cpu.yaml
│   ├── GPU
│   │   └── converter_args_gpu.yaml
│   ├── GPU_TFTRT
│   │   └── converter_args_gpu_tftrt.yaml
│   ├── VERSAL
│   │   └── converter_args_versal.yaml
│   ├── ZYNQ
│   │   └── converter_args_zynq.yaml
│   └── converter_args.yaml
├── dataloaders
│   ├── my_imagenet_dataloader.py
│   └── resnet50_dataloader.py
├── datasets
│   └── ImageNet_val_100
│       └── *(many image files)*
└── models
    └── ResNet50_ImageNet_70_90_7_76GF_2_3
        ├── assets
        ├── saved_model.pb
        └── variables
            ├── variables.data-00000-of-00001
            └── variables.index
```

## File Descriptions

### Configurations Directory

- **converter_args.yaml**: Contains the general arguments required for the Converter flow, applicable across all AI-framework/platform pairs.
- **converter_args_{pair}.yaml**: AI-framework/platform-specific arguments for the Converter flow. Each file includes parameters such as image name, model name, dataset name, dataloader name, paths, and output configurations.

### Dataloaders Directory

- **my_imagenet_dataloader.py**: Contains the function to create a TensorFlow dataset from ImageNet images.
- **resnet50_dataloader.py**: Contains the function to preprocess and load the ResNet50 dataset for quantization.

### Datasets Directory

- **ImageNet_val_100/**: Contains a sample dataset of 100 validation images from ImageNet, used for quantization during the conversion process.

### Models Directory

- **ResNet50_ImageNet_70_90_7_76GF_2_3/**: Contains the ResNet50 model files in the TensorFlow SavedModel format.

## Create Your Own Input Directory for Converter Flow

This Converter directory serves as a template for setting up the conversion flow for different AI-framework/platform pairs, using as input models saved in the TensorFlow SavedModel format. Follow these instructions to customize the directory for your specific needs:

### Step-by-Step Guide

1. **Adjust configuration YAML Files**:
    -Do not remove any `.yaml` files or change the names of their fields. Instead, adjust their values to match your specific configuration.
    -The `.yaml` files contain essential configuration parameters such as image name, model name, dataset name, dataloader name, paths, and output configurations.

2. **Prepare AI Model Files**:
    - Ensure that the required AI model files are added to the models subdirectory. These model files should be pre-trained and ready for conversion.

3. *(optional)* **Add the quantization dataset** 
    -  Ensure that the required dataset files are added to the dataset subdirectory.

4. *(optional)* **Implement Custom Logic in dataloaders**:
    - Modify the dataloader functions to suit your dataset requirements, but do not change their interfaces.
    - Ensure that the dataloaders return a tf.data.Dataset object as expected by the Converter flow.

## Conclusion

The Input Directory for the Converter module is essential for configuring and running AI model conversions on various hardware platforms. By providing AI-framework/platform combination-specific configuration files, datasets, and models, it ensures that models are converted efficiently and are compatible with the target hardware. This documentation offers a comprehensive overview of the core components and their roles, facilitating an understanding of the Converter flow and its customization for specific AI-framework/platform pairs.
