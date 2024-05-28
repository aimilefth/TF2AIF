# SEMSEG_LAT

## Overview

This project demonstrates the full capabilities of the TF2AIF tool, encompassing both the Converter and Composer flows. It provides all the necessary data, code, and configuration files to run the TF2AIF flow and generate UNET_v3 inference servers for various AI-framework/platform pairs.

The project includes TensorFlow models within the `Converter/models` directory and the dataset within the `Converter/datasets` directory. The TF2AIF_run flow initiates the Converter flow, which creates derived files in the `Converter/outputs` directory. Subsequently, the TF2AIF_run flow moves these derived files to the appropriate Composer directories. From there, the Composer flow assembles the containers.

## TF2AIF_args.yaml Configuration

The `TF2AIF_args.yaml` file contains configurations that are read by the `/src/TF2AIF_runs/TF2AIF_run_all.sh` script and passed to the individual `TF2AIF_run_${pair}.sh` scripts. The key configurations include:

```yaml
input_framework: TF
run_converter: True
run_composer: True
compose_native_TF: True
compose_native_PT: False

```
- input_framework: Specifies the framework of the input model, in this case, TensorFlow (TF).
- run_converter: Indicates whether to run the Converter flow.
- run_composer: Indicates whether to run the Composer flow.
- compose_native_TF: Indicates whether to compose native TensorFlow containers.
- compose_native_PT: Indicates whether to compose native PyTorch containers.

## Create your own Input Directory


This directory serves as a template for running the TF2AIF flow for different AI-framework/platform pairs on a specific TensorFlow AI model. To customize the flow for your needs, follow these steps:

### Step-by-Step Guide
1. **Adjust TF2AIF_args.yaml Values**:
    - Modify the values in the `TF2AIF_args.yaml` file to match your specific requirements. Ensure that the `input_framework`, `run_converter`, `run_composer`, `compose_native_TF`, and `compose_native_PT` values are set appropriately for your use case.

2. **Follow the Converter README**:
    - Navigate to `Converter/README.md` for detailed instructions on setting up and running the Converter flow. This includes preparing your models, datasets, and dataloaders, as well as configuring the necessary YAML files.

3. **Follow the Composer README**:
    - Navigate to `Composer/README.md` for detailed instructions on setting up and running the Composer flow. This includes configuring the platform-specific YAML files, adding additional libraries, and setting up environment variables.

## Conclusion

The CLASSIFICATION_THR directory provides a comprehensive template for leveraging the TF2AIF tool to convert and deploy AI models across various hardware platforms. By following the detailed instructions in the README files and adjusting the configuration files to suit your specific requirements, you can efficiently set up and run the TF2AIF flow for your AI models. The provided example of the UNET_v3 model serves as a guide to help you understand and implement the process for other models and AI-framework/platform pairs.