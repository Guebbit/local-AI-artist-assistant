# Local AI Artist Assistant (Sketch → Ink)

Artist-first local pipeline based on **Stable Diffusion WebUI (AUTOMATIC1111) + ControlNet**.

## What this gives you

- Local-only workflow after initial setup
- Podman container with CUDA for RTX 4090
- Preinstalled:
  - AUTOMATIC1111 (`--api --xformers`)
  - ControlNet extension
  - ADetailer extension
- 3 presets for one-click ink passes:
  - `CLEAN_INK`
  - `TATTOO_STENCIL`
  - `COMIC_INK`
- Optional REST API: `POST /inkify`

---

## Folder structure

```text
.
├── Containerfile
├── podman-compose.yml
├── .env.example
├── config/
│   ├── webui-user.sh
│   ├── ui-config.json
│   ├── styles.csv
│   └── presets/
│       ├── CLEAN_INK.json
│       ├── TATTOO_STENCIL.json
│       └── COMIC_INK.json
├── scripts/
│   ├── bootstrap_a1111.sh
│   ├── download_models.sh
│   └── run_preset_tests.py
├── api/
│   ├── requirements.txt
│   └── inkify_api.py
├── examples/
│   ├── input/
│   │   └── sample_sketch.png.base64
│   └── output/
└── outputs/
    └── test_runs/
```

---

## 1) Prerequisites (one-time)

- NVIDIA driver + CUDA runtime on host
- Podman + podman-compose
- NVIDIA container toolkit configured for Podman

---

## 2) Container run command (Podman preferred)

```bash
cd /path/to/local-AI-artist-assistant
cp .env.example .env
podman-compose up --build -d
```

UI port: `7860`  
Optional API port: `8000`

Open UI: `http://localhost:7860`

---

## 3) Start UI manually (alternative)

```bash
podman build -t local-a1111 -f Containerfile .
podman run --rm -it \
  --security-opt=label=disable \
  --device nvidia.com/gpu=all \
  -p 7860:7860 \
  -v "$(pwd)/data:/data:Z" \
  -v "$(pwd)/config:/config:Z,ro" \
  -v "$(pwd)/outputs:/outputs:Z" \
  local-a1111
```

---

## 4) Download models

Run inside the running `sd-webui` container:

```bash
podman exec -it sd-webui bash -lc "/workspace/scripts/download_models.sh"
```

Models are placed in:

- Base models: `/data/models/Stable-diffusion/`
- ControlNet models: `/data/models/ControlNet/`
- LoRAs: `/data/models/Lora/` (optional entries included)

---

## 5) Artist workflow (no coding)

1. Open browser: `http://localhost:7860`
2. Go to **img2img**
3. Upload your sketch
4. Pick style preset (`CLEAN_INK`, `TATTOO_STENCIL`, `COMIC_INK`)
5. Generate

Where to drop sketches:

- Put files in `examples/input/` (or anywhere local)
- Upload from UI

---

## 6) Pipeline test

Run all three presets and save outputs:

```bash
podman exec -it sd-webui python /workspace/scripts/run_preset_tests.py
```

Generated files:

- `/outputs/test_runs/CLEAN_INK.png`
- `/outputs/test_runs/TATTOO_STENCIL.png`
- `/outputs/test_runs/COMIC_INK.png`

---

## 7) Optional local REST API

Start with compose (enabled by default in `podman-compose.yml`), then call:

```bash
curl -X POST "http://localhost:8000/inkify" \
  -F "preset=CLEAN_INK" \
  -F "image=@examples/input/sample_sketch.png" \
  --output inked.png
```

---

## Notes

- First setup requires internet for cloning repos and model downloads.
- After setup, generation is local-only.
- Default generation settings are in `config/webui-user.sh` and `config/presets/*.json`.
- The startup script sets `PIP_NO_BUILD_ISOLATION=1` only for the `webui.sh` launch command to avoid known CLIP wheel build-isolation failures during first AUTOMATIC1111 dependency install.
