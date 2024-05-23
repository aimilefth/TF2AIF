#!/bin/bash

# Array of subdirectories
subdirs=(AGX ALVEO ARM Client CPU GPU AGX_TF ARM_TF CPU_TF GPU_TF)

# Iterate through each subdirectory and run docker_build.sh
for subdir in "${subdirs[@]}"; do
    if [ -d "$subdir" ] && [ -f "$subdir/docker_build.sh" ]; then
        echo "Building in directory: $subdir"
        cd "$subdir"
        bash docker_build.sh
        cd ..
    else
        echo "Skipping directory: $subdir (either directory or docker_build.sh does not exist)"
    fi
done
