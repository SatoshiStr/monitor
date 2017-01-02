#!/bin/bash
set -x
set -e

apt-get install -y curl apt-transport-https

echo 'deb https://packagecloud.io/grafana/stable/debian/ jessie main' >> /etc/apt/sources.list
curl https://packagecloud.io/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

service  grafana-server start
