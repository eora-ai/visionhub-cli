# ============ BEGIN Vision Hub API ============
FROM public.registry.visionhub.ru/models/base:v5 AS base
# ============ END Vision Hub API ============

# ============ BEGIN User model environment ============
FROM ubuntu:18.04

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev libglib2.0-0 ffmpeg && \
    apt-get install -y python3-pip && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
    pip install -r requirements.txt
# ============ END User model environment ============

# ============ BEGIN Vision Hub API ============
COPY --from=base /model_base /model_base
# Environment params for runner
ENV dataset_addr="tcp://*:5556"
ENV result_addr="tcp://*:5555"
ENV TEST_MODE=0
ENV BATCH_SIZE=1

# Install python requirements needed to run Vision Hub API
RUN pip install -r /model_base/requirements.txt
# Run command for docker container
# PARAMS for `container_runner.py`:
#   '--dataset_addr' - 'Address of socket to connect to the dataset queue'
#   '--dataset_sync_addr' - 'Address of a socket to synchornize with the dataset queue'
#   '--result_addr' - 'Address of a socket to connect to the results queue'
#   '--result_sync_addr' - 'Address of a socket to synchornize with the results queue'
#   '--TEST_MODE' - '1 if needed to run in test mode, 0 otherwise'
CMD python -u /model_base/container_runner.py --dataset_addr=${dataset_addr} \
                                              --result_addr=${result_addr} \
                                              --test_mode=$TEST_MODE --batch_size=$BATCH_SIZE
# ============ END Vision Hub API ============
