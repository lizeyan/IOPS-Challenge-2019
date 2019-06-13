#!/usr/bin/env bash

CONTEXT="$(dirname $(realpath $0))"
TEAM="re"
echo context: ${CONTEXT}
sudo docker build ${CONTEXT} -t ${TEAM}
sudo docker save example_user -o /srv/${TEAM}.tar