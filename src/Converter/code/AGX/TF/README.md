Source code for TF_AGX Converter docker container

Docker is built by:
docker buildx build -f ./Dockerfile --platform linux/amd64 --tag aimilefth/tf2aif_converter:tf_agx --push .

Execute on host with appropriate converter script file