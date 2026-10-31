#!/usr/bin/env bash
set -euo pipefail
# Только Linux/NVIDIA. Внутри контейнера следуй version-specific guide модуля 16.
docker run --rm -it --gpus all --shm-size=2g \
  -p 127.0.0.1:8000:8000 -p 127.0.0.1:8001:8001 -p 127.0.0.1:8002:8002 \
  nvcr.io/nvidia/tritonserver:25.06-trtllm-python-py3 bash
