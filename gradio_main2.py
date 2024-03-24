import re
import threading

import gradio as gr
import random
import time

from agentscope.message import Msg
from loguru import logger

import random
import array as arr
import yaml

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

def pl_check_info():
    return "\n".join(scene_manager.get_player_check_info())
def npc_check_info():
    return "\n".join(scene_manager.get_npc_check_info())


def create():

    with open('attributes.yaml', 'w') as f:
        yaml.dump({}, f, default_flow_style=False)
    attributes = arr.array()
    for i in range(1,9):
        attributes[i] = random.randint(30, 70)
    yaml_string = yaml.dump(attributes)
    with open('attributes.yaml', 'w') as f:
        f.write(yaml_string)


with gr.Blocks(theme=gr.themes.Base()) as demo:
    with gr.Tab(label="kp"):
        with gr.Row():
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        dropdown_changeNpc = gr.Dropdown(["npc1", "npc2", "需要读后端数据"], label="人物",
                                                          min_width=1, scale=15)
                        changeNpc_btn = gr.Button("切换", min_width=1, scale=1)



                    with gr.Row():
                        gr.Image(type='filepath', label="插图", value=scene_manager.get_illustration_path, every=1)
                        with gr.Column():
                            with gr.Row():
                                str1 = gr.Textbox(label="力量",interactive=False,min_width=10)
                                con1 = gr.Textbox(label="体质",interactive=False,min_width=10)
                                siz1 = gr.Textbox(label="体型",interactive=False,min_width=10)
                            with gr.Row():
                                dex1 = gr.Textbox(label="敏捷",interactive=False,min_width=10)
                                app1 = gr.Textbox(label="外貌",interactive=False,min_width=10)
                                pow1 = gr.Textbox(label="意志",interactive=False,min_width=10)
                            with gr.Row():
                                int1 = gr.Textbox(label="智力",interactive=False,min_width=10)
                                edu1 = gr.Textbox(label="教育",interactive=False,min_width=10)
                                luc1 = gr.Textbox(label="幸运",interactive=False,min_width=10)
                            with gr.Row():
                                hp1 = gr.Textbox(label="hp",interactive=False,min_width=10)
                                mp1 = gr.Textbox(label="mp",interactive=False,min_width=10)
                                san1 = gr.Textbox(label="san",interactive=False,min_width=10)
                    skill1 = gr.Dataframe(col_count=(2,"fixed"), headers=["技能","数值"])
            with gr.Column():
                with gr.Row():
                    dropdown_changeArea = gr.Dropdown(["场地一", "场地二", "需要读后端数据"],label="场景",min_width=1,scale= 15)
                    changeArea_btn = gr.Button("切换",min_width=1,scale=1)
                output_for_kp = gr.Textbox(label="剧本历史", lines=10, autoscroll=True, value="script_for_pl", every=1,)
                kp_check_box = gr.Textbox(label="检定记录", lines=2, autoscroll=True, value="pl_check_info", every=1)
                with gr.Row():
                    kp_say_box = gr.Textbox(label="KP叙述",scale=15)
                    kp_submit_btn = gr.Button("提交叙述",min_width=1,scale=1)

                gr.Interface(fn=kp_submit_btn.click,inputs=[kp_say_box],outputs=output_for_kp,live=True)


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


    with gr.Tab(label="pl"):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    gr.Image(type='filepath', label="插图", value=scene_manager.get_illustration_path, every=1)
                    with gr.Column():
                        with gr.Row():
                            str2 = gr.Textbox(label="力量", interactive=False, min_width=10)
                            con2 = gr.Textbox(label="体质", interactive=False, min_width=10)
                            siz2 = gr.Textbox(label="体型", interactive=False, min_width=10)
                        with gr.Row():
                            dex2 = gr.Textbox(label="敏捷", interactive=False, min_width=10)
                            app2 = gr.Textbox(label="外貌", interactive=False, min_width=10)
                            pow2 = gr.Textbox(label="意志", interactive=False, min_width=10)
                        with gr.Row():
                            int2 = gr.Textbox(label="智力", interactive=False, min_width=10)
                            edu2 = gr.Textbox(label="教育", interactive=False, min_width=10)
                            luc2 = gr.Textbox(label="幸运", interactive=False, min_width=10)
                        with gr.Row():
                            hp2 = gr.Textbox(label="hp", interactive=False, min_width=10)
                            mp2 = gr.Textbox(label="mp", interactive=False, min_width=10)
                            san2 = gr.Textbox(label="san", interactive=False, min_width=10)
                skill2 = gr.Dataframe(col_count=(2, "fixed"), headers=["技能", "数值"])



            with gr.Column():
                output_for_pl = gr.Textbox(label="剧本历史", lines=10, autoscroll=True, value=script_for_pl, every=1)
                pl_check_box = gr.Textbox(label="检定记录", lines=2, autoscroll=True, value=pl_check_info, every=1)


                with gr.Row():
                    with gr.Column(scale=15):
                        player_act_box = gr.Textbox(label="行动")
                        player_say_box = gr.Textbox(label="发言")
                    pl_submit_btn = gr.Button("提交",min_width=1,scale=1)

                    gr.Interface(fn=pl_submit_btn.click, inputs=[player_name_box, player_act_box, player_say_box], outputs=output_for_pl, live=True)

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

demo.launch()