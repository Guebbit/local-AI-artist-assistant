#!/usr/bin/env bash
set -euo pipefail

DATA_DIR="${DATA_DIR:-/data}"
SD_DIR="${DATA_DIR}/models/Stable-diffusion"
CN_DIR="${DATA_DIR}/models/ControlNet"
LORA_DIR="${DATA_DIR}/models/Lora"

mkdir -p "${SD_DIR}" "${CN_DIR}" "${LORA_DIR}"

download_if_missing() {
  local url="$1"
  local target="$2"
  if [ ! -f "${target}" ]; then
    echo "Downloading $(basename "${target}")..."
    wget -q --show-progress -O "${target}" "${url}"
  else
    echo "Already present: $(basename "${target}")"
  fi
}

# Base models
download_if_missing \
  "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" \
  "${SD_DIR}/v1-5-pruned-emaonly.safetensors"

# Optional SDXL base
if [ "${DOWNLOAD_SDXL:-1}" = "1" ]; then
  if ! download_if_missing \
    "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
    "${SD_DIR}/sd_xl_base_1.0.safetensors"; then
    echo "WARNING: SDXL download failed. Continuing with SD1.5 only."
  fi
fi

# ControlNet models
download_if_missing \
  "https://huggingface.co/lllyasviel/control_v11p_sd15_lineart/resolve/main/diffusion_pytorch_model.safetensors" \
  "${CN_DIR}/control_v11p_sd15_lineart.safetensors"
download_if_missing \
  "https://huggingface.co/lllyasviel/control_v11p_sd15_scribble/resolve/main/diffusion_pytorch_model.safetensors" \
  "${CN_DIR}/control_v11p_sd15_scribble.safetensors"
download_if_missing \
  "https://huggingface.co/lllyasviel/control_v11p_sd15_canny/resolve/main/diffusion_pytorch_model.safetensors" \
  "${CN_DIR}/control_v11p_sd15_canny.safetensors"

# Optional LoRAs (set URLs in env for one-shot download)
[ -n "${LORA_LINEART_ENHANCER_URL:-}" ] && download_if_missing "${LORA_LINEART_ENHANCER_URL}" "${LORA_DIR}/lineart_enhancer.safetensors"
[ -n "${LORA_TATTOO_STYLE_URL:-}" ] && download_if_missing "${LORA_TATTOO_STYLE_URL}" "${LORA_DIR}/tattoo_style.safetensors"
[ -n "${LORA_MANGA_INK_URL:-}" ] && download_if_missing "${LORA_MANGA_INK_URL}" "${LORA_DIR}/manga_ink.safetensors"

echo "Model download step completed."
