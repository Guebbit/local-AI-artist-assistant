#!/usr/bin/env bash
set -euo pipefail

WEBUI_DIR="${WEBUI_DIR:-/opt/stable-diffusion-webui}"
DATA_DIR="${DATA_DIR:-/data}"
CONFIG_DIR="/config"
WORKSPACE_DIR="/workspace"

setup_webui() {
  if [ ! -d "${WEBUI_DIR}/.git" ]; then
    git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git "${WEBUI_DIR}"
  fi

  mkdir -p \
    "${DATA_DIR}/models/Stable-diffusion" \
    "${DATA_DIR}/models/ControlNet" \
    "${DATA_DIR}/models/Lora" \
    "${DATA_DIR}/extensions" \
    "${DATA_DIR}/outputs" \
    /outputs/test_runs

  if [ ! -d "${WEBUI_DIR}/extensions/sd-webui-controlnet/.git" ]; then
    git clone https://github.com/Mikubill/sd-webui-controlnet.git "${WEBUI_DIR}/extensions/sd-webui-controlnet"
  fi

  if [ ! -d "${WEBUI_DIR}/extensions/adetailer/.git" ]; then
    git clone https://github.com/Bing-su/adetailer.git "${WEBUI_DIR}/extensions/adetailer"
  fi

  ln -sfn "${DATA_DIR}/models/Stable-diffusion" "${WEBUI_DIR}/models/Stable-diffusion"
  ln -sfn "${DATA_DIR}/models/ControlNet" "${WEBUI_DIR}/models/ControlNet"
  ln -sfn "${DATA_DIR}/models/Lora" "${WEBUI_DIR}/models/Lora"
  ln -sfn "${DATA_DIR}/outputs" "${WEBUI_DIR}/outputs"

  if [ -f "${CONFIG_DIR}/styles.csv" ]; then
    cp "${CONFIG_DIR}/styles.csv" "${WEBUI_DIR}/styles.csv"
  fi
  if [ -f "${CONFIG_DIR}/ui-config.json" ]; then
    cp "${CONFIG_DIR}/ui-config.json" "${WEBUI_DIR}/ui-config.json"
  fi
  if [ -f "${CONFIG_DIR}/config.json" ]; then
    cp "${CONFIG_DIR}/config.json" "${WEBUI_DIR}/config.json"
  fi
}

run_webui() {
  setup_webui
  cd "${WEBUI_DIR}"
  export COMMANDLINE_ARGS="--listen --port 7860 --api --xformers --ckpt-dir ${DATA_DIR}/models/Stable-diffusion --controlnet-dir ${DATA_DIR}/models/ControlNet --lora-dir ${DATA_DIR}/models/Lora --styles-file /config/styles.csv"
  export WEBUI_CONFIG_FILE="${CONFIG_DIR}/webui-user.sh"
  if [ -f "${CONFIG_DIR}/webui-user.sh" ]; then
    cp "${CONFIG_DIR}/webui-user.sh" "${WEBUI_DIR}/webui-user.sh"
  fi
  PIP_NO_BUILD_ISOLATION=1 ./webui.sh -f
}

if [ "${1:-}" = "run" ]; then
  run_webui
else
  setup_webui
fi
