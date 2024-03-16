from http import HTTPStatus
from pathlib import PurePosixPath
from urllib.parse import unquote, urlparse
import os

os.environ["DASHSCOPE_API_KEY"] = "sk-d1c122e76c8a4d11b78b3734e48960c6"
import agentscope
import dashscope
import requests
from agentscope.agents import DialogAgent, UserAgent
from agentscope.models import load_model_by_config_name
from dashscope import ImageSynthesis

model_configs = [
    {
        "config_name": "qwen-turbo",
        "model_type": "tongyi_chat",
        "model_name": "qwen-turbo",
        "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "api_key": "sk-d1c122e76c8a4d11b78b3734e48960c6",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "sk-d1c122e76c8a4d11b78b3734e48960c6"
        },
        "messages_key": "input"
    },
    {
        "config_name": "stable-diffusion-xl-size-1024x1024",
        "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis",
        "model_type": "dashscope_image_synthesis",
        "model_name": "stable-diffusion-xl",
        "api_key": "sk-d1c122e76c8a4d11b78b3734e48960c6",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "sk-d1c122e76c8a4d11b78b3734e48960c6"
        },
        "generate_args": {
            "size": "1024x1024",
            "seed": 42
        }
    },
    # Additional models can be configured here
]

rsp = ImageSynthesis.call(model=ImageSynthesis.Models.wanx_v1,
                          prompt="1gril,cowboy_shot",
                          n=4,
                          size='1024*1024')
if rsp.status_code == HTTPStatus.OK:
    print(rsp.output)
    print(rsp.usage)
    # save file to current directory
    for result in rsp.output.results:
        file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
        with open('./%s' % file_name, 'wb+') as f:
            f.write(requests.get(result.url).content)
else:
    print('Failed, status_code: %s, code: %s, message: %s' %
          (rsp.status_code, rsp.code, rsp.message))

agentscope.init(model_configs=model_configs)

dialogAgent = DialogAgent(name="assistant", model_config_name="qwen-turbo", sys_prompt="你是一个友善的对话AI机器人")
userAgent = UserAgent()
x = None
while True:
    x = dialogAgent(x)
    x = userAgent(x)

    # Terminate the conversation if the user types "exit"
    if x.content == "exit":
        print("Exiting the conversation.")
        break
