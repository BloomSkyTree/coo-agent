import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin
from loguru import logger

from configuration import PROJECT_GLOBAL_CONFIG
from utils.json_utils import extract_json
from utils.llm.LlmFactory import LlmFactory
from utils.llm.LlmMessage import LlmMessage


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


def generate_character_tags(description, auto_retry_times=3):
    llm = LlmFactory.get_llm_by_model_name("autodl_llama", system_prompt=[
        LlmMessage(
            role="system",
            content="按照给出的人物外貌描述，给出对应的英文stable diffusion正面标签。回答时，使用json数组形式。必须以英文回答。")
    ])
    message_content = llm.chat(query=LlmMessage(content=f"人物外貌描述：{description}"), max_new_tokens=512).content
    while auto_retry_times > 0:
        try:
            result = extract_json(message_content)
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], str):
                return result
            auto_retry_times -= 1
        except Exception as e:
            logger.exception(e)
            auto_retry_times -= 1
    return ["生成失败，请重新尝试"]

def generate_scene_tags(description, auto_retry_times=3):
    llm = LlmFactory.get_llm_by_model_name("autodl_llama", system_prompt=[
        LlmMessage(
            role="system",
            content="按照给出的场景描述，给出对应的英文stable diffusion正面标签。回答时，使用json数组形式。必须以英文回答。")
    ])
    message_content = llm.chat(query=LlmMessage(content=f"场景描述：{description}"), max_new_tokens=512).content
    while auto_retry_times > 0:
        try:
            result = extract_json(message_content)
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], str):
                return result
            auto_retry_times -= 1
        except Exception as e:
            logger.exception(e)
            auto_retry_times -= 1
    return ["生成失败，请重新尝试"]