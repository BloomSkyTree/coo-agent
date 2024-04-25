import os
import re

import gradio as gr
from agentscope.message import Msg

from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter


def selectable_player_names(config_root_path):
    directory = config_root_path + "/characters/player_characters"
    player_names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            player_names.append(filename.replace(".yaml", ""))
    return player_names


def get_character_avatar(config_root_path, character_name):
    directory = config_root_path + "/images"
    if os.path.isfile(os.path.join(directory, character_name + ".png")):
        return os.path.join(directory, character_name + ".png")
    return None


def get_character(config_root_path, character_name):
    player_path = config_root_path + f"/characters/player_characters/{character_name}.yaml"
    npc_path = config_root_path + f"/characters/non_player_characters/{character_name}.yaml"
    character = None
    if os.path.exists(player_path):
        character = PlayerCharacter(config_path=player_path)
    elif os.path.exists(npc_path):
        character = NonPlayerCharacter(config_path=npc_path)
    return character


def get_selectable_character_ability_and_skill(config_root_path, character_name):
    character = get_character(config_root_path, character_name)
    if character is None:
        return []
    ability_and_skill = character.get_ability_and_skill()
    dataframe = []
    for key in ability_and_skill:
        dataframe.append([key, ability_and_skill[key]])
    return dataframe




def generate_player_layout(config_root_path, scene_manager):
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

    def pl_check_info():
        return "\n".join(scene_manager.get_player_check_info())

    for player_name in selectable_player_names(config_root_path):

        with gr.Tab(label=player_name):
            with gr.Row():
                with gr.Column():
                    gr.Image(type='filepath', label="头像", value=get_character_avatar(config_root_path, player_name),
                             height=300)
                    ability_and_skill_for_pl = gr.Dataframe(headers=["属性/技能", "数值"],
                                                            value=get_selectable_character_ability_and_skill(
                                                                config_root_path,
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
