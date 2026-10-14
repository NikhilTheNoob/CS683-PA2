#!/bin/bash
# Full Task 2b pipeline: build all configs, run all traces, make tables/plots.
# Meant to be run in the GCC 7 container:  ./docker/run.sh ./docs/2b/scripts/all.sh
set -e
cd "$(dirname "$0")/../../.."
g++ --version | head -1
./docs/2b/scripts/build.sh
./docs/2b/scripts/run.sh
python3 docs/2b/scripts/plot.py
