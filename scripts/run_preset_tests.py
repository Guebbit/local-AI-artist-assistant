import base64
import json
from pathlib import Path

import requests


ROOT = Path("/workspace")
PRESETS_DIR = ROOT / "config" / "presets"
OUTPUT_DIR = Path("/outputs/test_runs")
EXAMPLE_B64 = ROOT / "examples" / "input" / "sample_sketch.png.base64"
API_URL = "http://127.0.0.1:7860/sdapi/v1/img2img"


def load_sample_image() -> str:
    content = EXAMPLE_B64.read_text(encoding="utf-8").strip()
    return content


def payload_from_preset(preset_path: Path, image_b64: str) -> dict:
    preset = json.loads(preset_path.read_text(encoding="utf-8"))
    return {
        "prompt": preset["prompt"],
        "negative_prompt": preset.get("negative_prompt", ""),
        "sampler_name": preset.get("sampler_name", "DPM++ 2M Karras"),
        "steps": preset.get("steps", 20),
        "cfg_scale": preset.get("cfg_scale", 6),
        "denoising_strength": preset["denoising_strength"],
        "width": 1024,
        "height": 1024,
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
                        "guidance_end": 1.0,
                        "control_mode": "Balanced"
                    }
                ]
            }
        }
    }


def run():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sample_b64 = load_sample_image()

    for preset_path in sorted(PRESETS_DIR.glob("*.json")):
        payload = payload_from_preset(preset_path, sample_b64)
        response = requests.post(API_URL, json=payload, timeout=600)
        response.raise_for_status()
        data = response.json()
        if not data.get("images"):
            raise RuntimeError(f"No image returned for preset {preset_path.stem}")

        image_bytes = base64.b64decode(data["images"][0])
        out_file = OUTPUT_DIR / f"{preset_path.stem}.png"
        out_file.write_bytes(image_bytes)
        print(f"Saved {out_file}")


if __name__ == "__main__":
    run()
