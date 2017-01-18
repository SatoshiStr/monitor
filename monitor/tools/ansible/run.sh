#!/usr/bin/env bash

ansible-playbook playbook.yml -i hosts \
    -e @globals.yml
