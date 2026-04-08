import base64
import json
from pathlib import Path

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response


PRESETS_DIR = Path("/config/presets")
PRESET_FILES = {
    "CLEAN_INK": PRESETS_DIR / "CLEAN_INK.json",
    "TATTOO_STENCIL": PRESETS_DIR / "TATTOO_STENCIL.json",
    "COMIC_INK": PRESETS_DIR / "COMIC_INK.json",
}
SD_API = "http://sd-webui:7860/sdapi/v1/img2img"

app = FastAPI(title="Local Inkify API")


def load_preset(name: str) -> dict:
    preset_file = PRESET_FILES.get(name)
    if preset_file is None:
        raise HTTPException(status_code=404, detail=f"Preset '{name}' not found.")
    if not preset_file.exists():
        raise HTTPException(status_code=404, detail=f"Preset '{name}' not found.")
    return json.loads(preset_file.read_text(encoding="utf-8"))


def make_payload(preset: dict, image_b64: str) -> dict:
    try:
        controlnet = preset["controlnet"]
        module = controlnet["module"]
        model = controlnet["model"]
        weight = controlnet["weight"]
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"Preset is missing required field: {exc}") from exc

    return {
        "prompt": preset["prompt"],
        "negative_prompt": preset.get("negative_prompt", ""),
        "sampler_name": preset.get("sampler_name", "DPM++ 2M Karras"),
        "steps": preset.get("steps", 20),
        "cfg_scale": preset.get("cfg_scale", 6),
        "denoising_strength": preset["denoising_strength"],
        "width": preset.get("width", 1024),
        "height": preset.get("height", 1024),
        "init_images": [image_b64],
        "alwayson_scripts": {
            "controlnet": {
                "args": [
                    {
                        "enabled": True,
                        "input_image": image_b64,
                        "module": module,
                        "model": model,
                        "weight": weight,
                        "pixel_perfect": True,
                        "guidance_start": 0.0,
                        "guidance_end": 1.0,
                        "control_mode": "Balanced"
                    }
                ]
            }
        }
    }


@app.post("/inkify")
async def inkify(image: UploadFile = File(...), preset: str = Form(...)):
    preset_data = load_preset(preset)
    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Image file is empty.")

    image_b64 = base64.b64encode(raw).decode("utf-8")
    payload = make_payload(preset_data, image_b64)
    r = requests.post(SD_API, json=payload, timeout=600)

    if r.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"WebUI error: {r.text}")

    body = r.json()
    images = body.get("images", [])
    if not images:
        raise HTTPException(status_code=502, detail="No image returned by WebUI.")

    output = base64.b64decode(images[0])
    return Response(content=output, media_type="image/png")
