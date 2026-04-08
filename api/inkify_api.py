import base64
import json
from pathlib import Path
import re

import requests
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response


PRESETS_DIR = Path("/config/presets")
SD_API = "http://sd-webui:7860/sdapi/v1/img2img"

app = FastAPI(title="Local Inkify API")


def load_preset(name: str) -> dict:
    if not re.fullmatch(r"[A-Z0-9_]{1,64}", name):
        raise HTTPException(status_code=400, detail="Invalid preset name format.")

    preset_file = (PRESETS_DIR / f"{name}.json").resolve()
    if preset_file.parent != PRESETS_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid preset path.")
    if not preset_file.exists():
        raise HTTPException(status_code=404, detail=f"Preset '{name}' not found.")
    return json.loads(preset_file.read_text(encoding="utf-8"))


def make_payload(preset: dict, image_b64: str) -> dict:
    return {
        "prompt": preset["prompt"],
        "negative_prompt": preset.get("negative_prompt", ""),
        "sampler_name": preset.get("sampler_name", "DPM++ 2M Karras"),
        "steps": preset.get("steps", 20),
        "cfg_scale": preset.get("cfg_scale", 6),
        "denoising_strength": preset["denoising_strength"],
        "init_images": [image_b64],
        "alwayson_scripts": {
            "controlnet": {
                "args": [
                    {
                        "enabled": True,
                        "input_image": image_b64,
                        "module": preset["controlnet"]["module"],
                        "model": preset["controlnet"]["model"],
                        "weight": preset["controlnet"]["weight"],
                        "pixel_perfect": True,
                        "guidance_start": 0.0,
                        "guidance_end": 1.0
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
