#!/bin/bash
docker buildx build -f ./Dockerfile --platform linux/amd64 --tag aimilefth/aate_container_templates:gpu_tf --push .