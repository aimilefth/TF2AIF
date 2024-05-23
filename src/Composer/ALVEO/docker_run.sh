#!/bin/bash

IMAGE_NAME=$1
NAME=$2
PORT=$3

#uid=`id -u`
#gid=`id -g`

DETACHED="-it"

xclmgmt_driver="$(find /dev -name xclmgmt\*)"
docker_devices=""
for i in ${xclmgmt_driver} ;
do
  docker_devices+="--device=$i "
done

render_driver="$(find /dev/dri -name renderD\*)"
for i in ${render_driver} ;
do
  docker_devices+="--device=$i "
done

docker_run_params=(
    -v /dev/shm:/dev/shm
    -v /opt/xilinx/dsa:/opt/xilinx/dsa
    -v /opt/xilinx/overlaybins:/opt/xilinx/overlaybins
    -v /etc/xbutler:/etc/xbutler
    -v /scrape:/scrape
    -e VERSION=$VERSION
    --pull=always
    --rm
    --network=host
    --name=$NAME
    ${DETACHED}
)

# If PORT is not empty, add -e SERVER_PORT=${PORT} before image name
if [[ -n "$PORT" ]]; then
    docker_run_params+=("-e" "SERVER_PORT=${PORT}")
fi

docker_run_params+=($IMAGE_NAME)

docker run \
  $docker_devices \
  "${docker_run_params[@]}"