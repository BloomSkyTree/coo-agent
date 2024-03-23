import re
import threading

import gradio as gr
import random
import time

from agentscope.message import Msg
from loguru import logger

from scene.SceneManager import SceneManager

scene_manager = SceneManager("files")


def script_for_pl():
    script = scene_manager.get_script()
    visible_script = []
    for message in script:
        content = message["content"]
        content = re.sub(r"\n+", "\n", content)

        if message["name"] == "Keeper":

            content = re.sub(r"[\(（].*?[\)）]", "", content)
            if content.strip():
                visible_script.append(Msg(name=message["name"], content=content))
        else:
            visible_script.append(Msg(name=message["name"], content=content))

    return "\n\n".join([f"{m['content']}" for m in visible_script])


def script_for_kp():
    script = scene_manager.get_script()
    for message in script:
        content = message["content"]
        message["content"] = re.sub(r"\n+", "\n", content)
    return "\n\n".join([f"{m['name']}\n{m['content']}" for m in script])


with gr.Blocks() as app:
    with gr.Row():
        with gr.Column():
            player_name_box = gr.Textbox(label="角色名称")
            player_act_box = gr.Textbox(label="行动")
            player_say_box = gr.Textbox(label="发言")
            pl_submit_btn = gr.Button("提交行动")
        output_for_pl = gr.Textbox(label="剧本历史", lines=10, autoscroll=True, value=script_for_pl, every=1)


    @pl_submit_btn.click(inputs=[player_name_box, player_act_box, player_say_box])
    def pl_submit(name, act, say):
        if act.strip() == "" and say.strip() == "":
            return
        rp = ""
        if act.strip() != "":
            rp += f"（{act}）"
        if say.strip() != "":
            rp += f"“{say}”"
        scene_manager.player_role_play(name, rp)
        player_act_box.value = ""
        player_say_box.value = ""


    with gr.Row():
        with gr.Column():
            kp_say_box = gr.Textbox(label="KP叙述")
            kp_submit_btn = gr.Button("提交叙述")
        output_for_kp = gr.Textbox(label="剧本历史", lines=10, autoscroll=True, value=script_for_kp, every=1)


    @kp_submit_btn.click(inputs=[kp_say_box])
    def kp_submit(kp_say):
        kp_say_box.value = ""
        kp_message = Msg(
            name="Keeper",
            content=kp_say
        )
        python_code = scene_manager(kp_message)["content"]
        if "`" in python_code:
            python_code = "\n".join([line for line in python_code.split("\n") if not line.startswith("`")])
        try:
            exec(python_code)
        except Exception as e:
            logger.exception(e)
            logger.error(f"尝试执行以下python代码失败：{python_code}")


    gr.Image(type='filepath', label="插图", value=scene_manager.get_illustration_path, every=1)


app.launch()
