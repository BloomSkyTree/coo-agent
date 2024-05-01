import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

from configuration import PROJECT_GLOBAL_CONFIG


def draw(prompt,
         negative_prompt=PROJECT_GLOBAL_CONFIG["stable_diffusion"]["default_negative_prompt"],
         steps=32,
         sampler_name="Euler A SGMUniform",
         width=1024, height=1024, restore_faces=True):
    url = PROJECT_GLOBAL_CONFIG["stable_diffusion"]["url"]
    option_payload = {
        "sd_model_checkpoint": PROJECT_GLOBAL_CONFIG["stable_diffusion"]["model_name"],
        "CLIP_stop_at_last_layers": 2
    }
    requests.post(url=f'{url}/sdapi/v1/options', json=option_payload)
    payload = {
        "prompt": "masterpiece,best quality," + prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "sampler_name": sampler_name,
        "width": width,
        "height": height,
        "restore_faces": restore_faces
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()

    image_content = r["images"][0]
    image = Image.open(io.BytesIO(base64.b64decode(image_content.split(",", 1)[0])))

    png_payload = {
        "image": "data:image/png;base64," + image_content
    }
    image_response = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

    png_info = PngImagePlugin.PngInfo()
    png_info.add_text("parameters", image_response.json().get("info"))
    return image


if __name__ == '__main__':
    image = draw("1girl")
    image.save("test.png")
