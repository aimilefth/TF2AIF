#!/bin/bash
docker buildx build -f ./Dockerfile --platform linux/arm64 --tag aimilefth/aate_container_templates:arm --push .