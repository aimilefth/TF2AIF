#!/bin/bash
docker buildx build -f ./Dockerfile --platform linux/amd64,linux/arm64 --tag aimilefth/aate_container_templates:client --push .