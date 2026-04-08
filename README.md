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

## 5) Non-tech guide (after container is running)

### What can this do?

This tool takes a rough sketch and creates cleaner ink-style outputs locally on your machine.

- Turn pencil/rough lines into cleaner line art
- Try different ink looks quickly (`CLEAN_INK`, `TATTOO_STENCIL`, `COMIC_INK`)
- Iterate fast by regenerating variations from the same sketch
- Keep your work local (after initial setup/downloads)

### How can I ink my sketches?

1. Open `http://localhost:7860`
2. Go to **img2img**
3. Upload your sketch (PNG/JPG)
4. Choose a style preset: `CLEAN_INK`, `TATTOO_STENCIL`, or `COMIC_INK`
5. Click **Generate**
6. If needed, generate a few more times and keep your favorite output
7. Save the image from the WebUI

Where to put sketches:

- Any local folder works (upload manually in browser)
- Or keep inputs in `examples/input/` for organization

Where outputs go:

- In the WebUI output folder
- Also available in this repo under `outputs/` (mounted volume)

### For expert users (Krita and other non-Adobe tools)

You can keep your normal drawing workflow and use this project only for the inking pass.

- **Krita**: draw/export sketch as PNG → run through WebUI (`img2img`) → import result back as a new layer for cleanup.
- **GIMP**: same flow; use generated ink as a top layer and refine with masks/levels.
- **Inkscape**: run raster ink result through Trace Bitmap if you need vector-friendly linework.

Optional automation for advanced users:

- Use the local API (`POST /inkify`) to send images from scripts or custom tool integrations.

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
- The startup script sets `PIP_NO_BUILD_ISOLATION=1` only for the `webui.sh` launch command to avoid known `openai/CLIP` build-isolation failures during first AUTOMATIC1111 dependency install in the WebUI venv (this is a pip/CLIP packaging compatibility issue, not Podman-specific).
