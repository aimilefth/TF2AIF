# converter_alveo.sh

## Configuration Files

Running the converter script requires the existence and correctness of two configuration files:
1. `converter_args.yaml`: Contains environmental variables that are applicable to all AI-framework/platform pairs.
2. `converter_args_alveo.yaml`: Contains environmental variables that are specific to the ALVEO AI-framework/platform pair.

**Pro Tip**: Ensure the .yaml files end with an empty line to avoid parsing issues.

## Example Configuration Files

### Example `converter_args.yaml`

```yaml
IMAGE_NAME: aimilefth/tf2aif_converter
MODEL_NAME: ResNet50_ImageNet_70_90_7_76GF_2_3
TRAINED: True
DATASET_NAME: ImageNet_val_100
DATALOADER_NAME: resnet50_dataloader.py
MODELS_PATH: ../models
LOGS_PATH: ../logs
DATASETS_PATH: ../datasets
OUTPUTS_PATH: ../outputs
DATALOADERS_PATH: ../dataloaders

```

### Example `converter_args_alveo.yaml`

```yaml
ARCH: U280_L

```

## Environmental Variables

### From `converter_args.yaml`

- **IMAGE_NAME**: The name of the Docker image used for the conversion.
- **MODEL_NAME**: The name of the model to be converted.
- **TRAINED**: Indicates whether the model is trained (`True`) or not (`False`).
- **DATASET_NAME**: The name of the dataset used for quantization.
- **DATALOADER_NAME**: The name of the dataloader script used to load the dataset.
- **MODELS_PATH**: The relative path to the directory containing the model.
- **LOGS_PATH**: The relative path to the directory where logs will be saved.
- **DATASETS_PATH**: The relative path to the directory containing the datasets.
- **OUTPUTS_PATH**: The relative path to the directory where the output models will be saved.
- **DATALOADERS_PATH**: The relative path to the directory containing the dataloaders.

### From `converter_args_alveo.yaml`

- **ARCH**: The architecture type for ALVEO (`u280_l` or `u280_h`).