# GCC 7 build/run environment for ChampSim (the compiler the PA2 README expects).
# Ubuntu 18.04's default g++ is 7.5. python3-matplotlib is for the plot scripts.
FROM ubuntu:18.04

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential python3 python3-matplotlib xz-utils gzip \
 && rm -rf /var/lib/apt/lists/*

# matplotlib needs a writable config dir when the container runs as a non-root user
ENV MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /pa2
