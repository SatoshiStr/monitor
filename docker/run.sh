#!/bin/bash
set -e
set -x

if [ "$1" == 'install-docker' ]; then
    curl -sSL https://get.docker.io | bash
elif [ "$1" == 'change-source' ]; then
	echo "DOCKER_OPTS=\"--registry-mirror=https://pee6w651.mirror.aliyuncs.com\"" | sudo tee -a /etc/default/docker
	sudo service docker restart
elif [ "$1" == 'build' ]; then
    read -p 'Input local ip: ' LOCAL_IP
    docker build --build-arg LOCAL_IP=${LOCAL_IP} --tag mymonitor .
elif [ "$1" == 'run' ]; then
    docker run -itd --privileged --net=host -v $(pwd)/../monitor:/opt/monitor --name mymonitor mymonitor
elif [ "$1" == 'exec' ]; then
    docker exec -it mymonitor bash
elif [ "$1" == 'clear' ]; then
    docker kill mymonitor
    docker rm mymonitor
fi
