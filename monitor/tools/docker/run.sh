#!/bin/bash
set -e
set -x

if [ "$1" == 'install-docker' ]; then
    curl -sSL https://get.docker.io | bash
elif [ "$1" == 'build' ]; then
    docker build --tag mymonitor .
elif [ "$1" == 'run' ]; then
    docker run -itd --privileged --net=host --name mymonitor mymonitor
elif [ "$1" == 'clear' ]; then
    docker kill mymonitor
    docker rm mymonitor
fi
