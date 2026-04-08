FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV WEBUI_DIR=/opt/stable-diffusion-webui
ENV DATA_DIR=/data

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-venv python3.10-dev python3-pip \
    git wget curl ca-certificates libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cu121
RUN python -m pip install xformers==0.0.27.post2 fastapi==0.115.0 uvicorn==0.30.6 requests==2.32.3 python-multipart==0.0.22

WORKDIR /workspace
COPY . /workspace

RUN chmod +x /workspace/scripts/bootstrap_a1111.sh /workspace/scripts/download_models.sh
RUN /workspace/scripts/bootstrap_a1111.sh

EXPOSE 7860 8000

ENTRYPOINT ["bash", "/workspace/scripts/bootstrap_a1111.sh", "run"]
