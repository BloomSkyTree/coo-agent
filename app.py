import os
import re
import threading

import gradio as gr
import random
import time

from agentscope.message import Msg
from loguru import logger

from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from scene.SceneManager import SceneManager

config_root_path = "files"
scene_manager = SceneManager(config_root_path)

def get_character(character_name):
    player_path = config_root_path + f"/characters/player_characters/{character_name}.yaml"
    npc_path = config_root_path + f"/characters/non_player_characters/{character_name}.yaml"
    character = None
    if os.path.exists(player_path):
        character = PlayerCharacter(config_path=player_path)
    elif os.path.exists(npc_path):
        character = NonPlayerCharacter(config_path=npc_path)
    return character


def selectable_scene_names():
    directory = config_root_path + "/scenes"
    scene_names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            scene_names.append(filename.replace(".yaml", ""))
    return scene_names


def selectable_player_names():
    directory = config_root_path + "/characters/player_characters"
    player_names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            player_names.append(filename.replace(".yaml", ""))
    return player_names


def selectable_non_player_names():
    directory = config_root_path + "/characters/non_player_characters"
    names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            names.append(filename.replace(".yaml", ""))
    return names


def get_selectable_character_ability_and_skill(character_name):
    character = get_character(character_name)
    if character is None:
        return []
    ability_and_skill = character.get_ability_and_skill()
    dataframe = []
    for key in ability_and_skill:
        dataframe.append([key, ability_and_skill[key]])
    return dataframe


def get_character_avatar(character_name):
    directory = config_root_path + "/images"
    if os.path.isfile(os.path.join(directory, character_name + ".png")):
        return os.path.join(directory, character_name + ".png")
    return None


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
    return "\n".join(scene_manager.get_all_check_info())


# def get_character_memory(name):
#     if name is not None and get_character(name) is not None:
#         return "\n".join(get_character(name).get_memory())
#     return ""


with gr.Blocks() as app:
    for player_name in selectable_player_names():


        with gr.Tab(label=player_name):
            with gr.Row():
                with gr.Column():
                    gr.Image(type='filepath', label="头像", value=get_character_avatar(player_name), height=300)
                    ability_and_skill_for_pl = gr.Dataframe(headers=["属性/技能", "数值"],
                                                            value=get_selectable_character_ability_and_skill(
                                                                player_name))

                with gr.Column():
                    output_for_pl = gr.Textbox(label="剧本历史", lines=10, autoscroll=True, value=script_for_pl, every=1)
                    pl_check_box = gr.Textbox(label="检定记录", lines=2, autoscroll=True, value=pl_check_info, every=1)

                    with gr.Row():
                        with gr.Column(scale=15):
                            player_name_box = gr.Textbox(label="玩家名称", value=player_name)
                            player_act_box = gr.Textbox(label="行动")
                            player_say_box = gr.Textbox(label="发言")
                        pl_submit_btn = gr.Button("提交", min_width=1, scale=1)


                        @pl_submit_btn.click(inputs=[player_name_box, player_act_box, player_say_box],
                                             outputs=[player_act_box, player_say_box])
                        def pl_submit(name, act, say):
                            gr.Info("已接受输入，由于生成需要时间，请静候...")
                            if act.strip() == "" and say.strip() == "":
                                return
                            rp = ""
                            if act.strip() != "":
                                rp += f"（{act}）"
                            if say.strip() != "":
                                rp += f"“{say}”"
                            scene_manager.player_role_play(name, rp)
                            return ["", ""]

    with gr.Tab(label="Keeper"):

        with gr.Row():
            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        dropdown_select_npc = gr.Dropdown(choices=selectable_non_player_names(), label="人物",
                                                          min_width=1, scale=15)

                    npc_avatar = gr.Image(type='filepath', label="头像", height=300)
                    ability_and_skill_for_npc = gr.Dataframe(headers=["属性/技能", "数值"])


            @dropdown_select_npc.change(inputs=[dropdown_select_npc], outputs=ability_and_skill_for_npc)
            def on_dropdown_select_npc_change_set_dataframe(npc_name):
                return get_selectable_character_ability_and_skill(npc_name)


            @dropdown_select_npc.change(inputs=[dropdown_select_npc], outputs=npc_avatar)
            def on_dropdown_select_npc_change_set_npc_avatar(npc_name):
                return get_character_avatar(npc_name)


            with gr.Column():
                with gr.Row():
                    dropdown_scene = gr.Dropdown(choices=selectable_scene_names(),
                                                 label="场景", min_width=1,
                                                 scale=15)
                output_for_kp = gr.Textbox(label="剧本历史", lines=10, autoscroll=True, value=script_for_pl,
                                           every=1, )
                kp_check_box = gr.Textbox(label="检定记录", lines=2, autoscroll=True, value=pl_check_info, every=1)
                with gr.Row():
                    kp_say_box = gr.Textbox(label="KP叙述", scale=15)
                    kp_submit_btn = gr.Button("提交叙述", min_width=1, scale=1)
                with gr.Row():
                    kp_save_btn = gr.Button("存档", min_width=1, scale=1)
                    kp_reset_btn = gr.Button("删档", min_width=1, scale=1)


                @dropdown_scene.change(inputs=[dropdown_scene])
                def on_dropdown_scene_change(scene_name):
                    if scene_name:
                        gr.Info(f"切换场景：{scene_name}")
                        scene_manager.enter_scene(scene_name)


                @kp_submit_btn.click(inputs=[], outputs=[kp_say_box])
                def clear_kp_say_box():
                    gr.Info("已接受输入，由于生成需要时间，请静候...")
                    return ""
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


                @kp_save_btn.click()
                def on_save_btn_click():
                    gr.Info("执行存档，为场景生成场景记忆，为角色生成角色记忆...")
                    scene_manager.save()
                    gr.Info("存档完成。")


                @kp_reset_btn.click(outputs=[dropdown_scene])
                def on_reset_btn_click():
                    gr.Info("执行删档。所有角色的记忆都将被重置到初始状态。")
                    global scene_manager
                    scene_manager.reset()
                    scene_manager = SceneManager(config_root_path=config_root_path)
                    gr.Info("删档完成。")
                    return ""

    with gr.Tab(label="即时插图"):
        gr.Image(type='filepath', label="插图", value=scene_manager.get_illustration_path, every=1)

app.launch()
