#!/usr/bin/env bash

CONTEXT="$(dirname $(realpath $0))"
TEAM="example_user"
echo context: ${CONTEXT}
docker build ${CONTEXT} -t ${TEAM}
docker save example_user -o /srv/${TEAM}.tar