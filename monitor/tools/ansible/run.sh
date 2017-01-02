#!/usr/bin/env bash

CUR_DIR=$(pwd)
ANSIBLE_DIR=${CUR_DIR}/tools/ansible
#ANSIBLE_DIR=.
ansible-playbook ${ANSIBLE_DIR}/playbook.yml -i ${ANSIBLE_DIR}/hosts \
    -e @${ANSIBLE_DIR}/globals.yml