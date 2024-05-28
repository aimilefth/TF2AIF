# IMPLEMENT NEW PAIR

## Overview 

TF2AIF is designed to be inherently modular and extensible. Implementing a new AI-framework/platform pair involves adding the necessary components to the existing system. The following steps provide a guideline on how to construct those necessary components.

1. Choose a name for the AI-framework/platform pair. Suppose `NEW_PAIR`
2. Implement the Base container image subdirectory for `NEW_PAIR`
3. Implement the the Converter flow scripts and Converter Docker for `NEW_PAIR`
4. Implement the Composer flow scripts and Composer code for `NEW_PAIR`
5. Implement the TF2AIF flow script for `NEW_PAIR`

Using one of the already-implemented AI-framework/platform combinations as a template can be very helpful, especially when implementing a new AI-framework/platform pair for the first time.

### 1. Choose a name

Selecting a representative name for the pair is crucial because the TF2AIF tool relies heavily on consistent naming conventions for each AI-framework/platform combination. Suppose the name we choose for this new pair is `NEW_PAIR`.

### 2. Implement the Base container image subdirectory

The Base container image subdirectory should have the following structure:

```shell
NEW_PAIR
├── Dockerfile
└── docker_build.sh
```
#### `docker_build.sh`

The `docker_build.sh` script should contain the command with which the base container image will be built. One key detail is the platform choice, which should match the architecture of the `NEW_PAIR` platform (either `linux/amd64` or `linux/arm64`).

Example `docker_build.sh`

```bash
#!/bin/bash
docker buildx build -f ./Dockerfile --platform linux/amd64 --tag your_dockerhub_username/custom_image_name:new_pair --push .
```

### `Dockerfile`

The `Dockerfile` should serve as the baseline for the `NEW_PAIR` AI-framework/platform combination. It should implement the functionality needed for the AI-framework/platform combination. Additionally, it should include the following Python libraries:

```requirements.txt
opencv-python
requests
flask
redistimeseries *(optional)*
python-dotenv *(optional)*
```

### 3. Implement the the Converter flow scripts and Converter Docker

This is the directory structure and files necessary to be implemented:

```shell
Converter/
├── code
│   └── NEW_PAIR
│       ├── PT
│       │   ├── Dockerfile
│       │   ├── README.md
│       │   ├── converter.py
│       │   ├── logconfig.ini
│       │   └── script.sh
│       └── TF
│           ├── Dockerfile
│           ├── README.md
│           ├── converter.py
│           ├── logconfig.ini
│           └── script.sh
└── converters
    └── NEW_PAIR
        ├── README.md
        └── converter_new_pair.sh
```

#### Composer Docker

The Composer Docker for `NEW_PAIR` should implement the following functionality (for either PT or TF input frameworks):

- Load a model and return the same model in the appropriate format based on the specified AI-framework.
- Comply with the Converter Docker structure, using certain environmental variables for configuration.
- Integrate with the existing quantization infrastructure if quantization is required.

The Converter Docker should be built and pushed to the appropriate remote repository. Building a correct Converter Docker is one of the most challenging parts of implementing a new AI-framework/platform combination. However, following the existing Converter Dockers as templates and modifying them can alleviate some of the difficulty.

#### Converter script `converter_new_pair.sh`

The Converter flow scripts are created with reproducibility, modularity, and extensibility in mind. Adjusting one of the existing Converter scripts should be simple if done carefully. Change the `NAME` variable and configure the `files` and `variables` arrays to ensure the necessary components are implemented.

### 4. Implement the Composer flow scripts and Composer code

This is the directory structure and files necessary to be implemented:

```shell
Composer
└── NEW_PAIR
    ├── Dockerfile.new_pair
    ├── composer_new_pair.sh
    ├── my_server.py
    └── new_pair_server.py
```

Be careful with the naming conventions, as correct naming is vital for the correct execution of the Composer flow and TF2AIF flow scripts.

#### `Dockerfile.new_pair`

The Dockerfile used for the Composer flow should start from the `NEW_PAIR` base container image, include the necessary environment variables, and copy the appropriate server files. Using one of the existing Dockerfiles as a template is recommended, as it minimizes both effort and the chance of error.

#### `composer_new_pair.sh`

The Composer flow scripts are created with reproducibility, modularity, and extensibility in mind. Adjusting one of the existing Composer scripts should be simple if done carefully. Change the `NAME` variable and configure the `files` and `variables` arrays to ensure the necessary components are implemented.

#### `new_pair_server.py`

The most important code file of the Composer flow. It creates a class `NewPairServer` that implements the necessary server methods. The implementation needs to follow the specifications imposed by the AI-framework and the platform choice (e.g., AI-framework library). Be careful to comply with the input/output specifications of each `NewPairServer` method according to the comments and documentation.

#### `my_server.py`

Example implementation of `my_server.py` file

```python
import new_pair_server

class MyServer(new_pair_server.NewPairServer):
    def __init__(self, logger):
        super().__init__(logger)
```

### 5. Implement the TF2AIF flow script

This is the directory structure and files necessary to be implemented

```shell
TF2AIF_runs
└── NEW_PAIR
    ├── TF2AIF_run_new_pair.sh
    └── README.md
```

#### TF2AIF_run_new_pair.sh

The TF2AIF flow scripts are created with reproducibility, modularity, and extensibility in mind. Adjusting one of the existing TF2AIF_run scripts should be simple if done carefully. Essentially, only two key modifications need to be made:

1. Change the `NAME` variable
2. Modify the code that moves the files from the outputs of the Converter flow to the appropriate subdirectories of the Composer flow and updates the YAML configuration files. This can be achieved by modifying the `extensions` and the `ext_to_arg` arrays appropriately. However, in some cases, further code adjustments might be necessary, depending on your AI-framework/platform combination intricacies.

Also remember to update the [`TF2AIF_runs.sh`](src/TF2AIF_runs/TF2AIF_runs.sh), [`docker_runs.sh`](src/TF2AIF_runs/docker_runs.sh), and [`clear_inputs.sh`](src/TF2AIF_runs/clear_inputs.sh) scripts, by including `NEW_PAIR` into the scripts.

## Conclusion

By following these steps and using the existing AI-framework/platform combinations as templates, you can implement a new AI-framework/platform pair in the TF2AIF tool. This process ensures that your new pair will integrate smoothly into the existing infrastructure, benefiting from the modular and extensible design of the TF2AIF project.