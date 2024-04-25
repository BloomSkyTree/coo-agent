import os
import re

import gradio as gr
from agentscope.message import Msg
from loguru import logger

from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from scene.SceneManager import SceneManager


def selectable_non_player_names(config_root_path):
    directory = config_root_path + "/characters/non_player_characters"
    names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            names.append(filename.replace(".yaml", ""))
    return names


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


def get_character_avatar(config_root_path, character_name):
    directory = config_root_path + "/images"
    if os.path.isfile(os.path.join(directory, character_name + ".png")):
        return os.path.join(directory, character_name + ".png")
    return None


def selectable_scene_names(config_root_path):
    directory = config_root_path + "/scenes"
    scene_names = []
    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)):
            scene_names.append(filename.replace(".yaml", ""))
    return scene_names


def define_keeper_layout(config_root_path, scene_manager):
    def script_for_kp():
        script = scene_manager.get_script()
        for message in script:
            content = message["content"]
            message["content"] = re.sub(r"\n+", "\n", content)
        return "\n\n".join([f"{m['name']}\n{m['content']}" for m in script])

    def all_check_info():
        return "\n".join(scene_manager.get_all_check_info())

    with gr.Tab(label="Keeper"):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    dropdown_select_npc = gr.Dropdown(choices=selectable_non_player_names(config_root_path), label="人物",
                                                      min_width=1, scale=15)
                with gr.Row():
                    with gr.Column():
                        npc_avatar = gr.Image(type='filepath', label="头像", height=300)
                    with gr.Column():
                        # kp_npc_enter_btn = gr.Button("人物入场")
                        kp_npc_illustrate_btn = gr.Button("描述外貌")
                        kp_npc_act_box = gr.Textbox(label="NPC角色扮演提示词", lines=6)
                        kp_npc_role_play_btn = gr.Button("角色扮演")
                ability_and_skill_for_npc = gr.Dataframe(headers=["属性/技能", "数值"])

            @dropdown_select_npc.change(inputs=[dropdown_select_npc], outputs=ability_and_skill_for_npc)
            def on_dropdown_select_npc_change_set_dataframe(npc_name):
                return get_selectable_character_ability_and_skill(config_root_path, npc_name)

            @dropdown_select_npc.change(inputs=[dropdown_select_npc], outputs=npc_avatar)
            def on_dropdown_select_npc_change_set_npc_avatar(npc_name):
                return get_character_avatar(config_root_path, npc_name)

            @kp_npc_illustrate_btn.click(inputs=[dropdown_select_npc])
            def on_kp_npc_illustrate_btn_click(npc_name):
                gr.Info(f"生成外貌描述：{npc_name}")
                scene_manager.character_outlook(npc_name)

            @kp_npc_role_play_btn.click(inputs=[dropdown_select_npc, kp_npc_act_box])
            def kp_npc_role_play(npc_name, npc_act):
                gr.Info(f"{npc_name} 进行角色扮演：{npc_act}")
                kp_npc_act_box.value = ""
                scene_manager.character_act(npc_name, npc_act)

            with gr.Column():
                with gr.Row():
                    dropdown_scene = gr.Dropdown(choices=selectable_scene_names(config_root_path),
                                                 label="场景", scale=8)
                    kp_illustrate_panorama_btn = gr.Button("绘制全景", scale=1)
                with gr.Row():
                    with gr.Column(scale=3):
                        output_for_kp = gr.Textbox(label="剧本历史",
                                                   lines=10,
                                                   autoscroll=True,
                                                   value=script_for_kp,
                                                   every=1)
                        kp_check_box = gr.Textbox(label="检定记录",
                                                  lines=2,
                                                  autoscroll=True,
                                                  value=all_check_info, every=1)

                with gr.Row():
                    kp_say_box = gr.Textbox(label="KP叙述", scale=15)
                    kp_submit_btn = gr.Button("提交叙述", min_width=1, scale=1)
                    kp_judge_check = gr.Button("判断检定", min_width=1, scale=1)
                with gr.Row():
                    kp_save_btn = gr.Button("存档", min_width=1, scale=1)
                    kp_reset_btn = gr.Button("删档", min_width=1, scale=1)

                @dropdown_scene.change(inputs=[dropdown_scene])
                def on_dropdown_scene_change(scene_name):
                    if scene_name:
                        gr.Info(f"切换场景：{scene_name}")
                        scene_manager.enter_scene(scene_name)

                @kp_illustrate_panorama_btn.click(inputs=[], outputs=[kp_say_box])
                def kp_illustrate_panorama():
                    gr.Info("生成场景描述...")
                    scene_manager.draw_a_panorama()

                @kp_submit_btn.click(inputs=[kp_say_box])
                def kp_submit(kp_say):
                    kp_say_box.value = ""
                    kp_message = Msg(
                        name="Keeper",
                        content=kp_say
                    )
                    scene_manager(kp_message)

                @kp_save_btn.click()
                def on_save_btn_click():
                    gr.Info("执行存档，为场景生成场景记忆，为角色生成角色记忆...")
                    scene_manager.save()
                    gr.Info("存档完成。")

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
