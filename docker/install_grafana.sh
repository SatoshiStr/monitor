#!/bin/bash
set -x
set -e

#apt-get install -y curl apt-transport-https
#
#echo 'deb https://packagecloud.io/grafana/stable/debian/ jessie main' >> /etc/apt/sources.list
#curl https://packagecloud.io/gpg.key | sudo apt-key add -
#sudo apt-get update
#sudo apt-get install grafana
sudo apt-get install -y wget dpkg
wget https://grafanarel.s3.amazonaws.com/builds/grafana_4.0.2-1481203731_amd64.deb
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i grafana_4.0.2-1481203731_amd64.deb

service  grafana-server start
