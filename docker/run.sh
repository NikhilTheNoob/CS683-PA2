#!/bin/bash
# Run a command inside the GCC 7 container with the repo mounted at /pa2.
# Builds the image on first use. Files are created as the calling user.
#   ./docker/run.sh g++ --version
#   ./docker/run.sh ./docs/2b/scripts/all.sh
set -e
cd "$(dirname "$0")/.."
IMAGE=cs683-pa2-gcc7
if ! docker image inspect $IMAGE > /dev/null 2>&1; then
    docker build -t $IMAGE docker/
fi
exec docker run --rm --user "$(id -u):$(id -g)" -v "$PWD":/pa2 $IMAGE "$@"
