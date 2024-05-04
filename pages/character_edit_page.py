import re
import uuid

import pandas as pd
import streamlit as st
import yaml
from PIL.Image import Image

from game import get_game
from game.GameManager import GameManager
from utils.file_system_utils import check_directory, copy_and_rename_directory, file_exists
from utils.stable_diffusion_utils import draw, generate_character_tags
from utils.voicevox_utils import get_speaker_names

ability_names = ["力量", "体质", "体型", "敏捷", "外貌", "智力", "意志", "教育", "幸运", "生命", "魔法", "理智", "理智上限"]
skill_names = ["侦查", "图书馆使用", "聆听", "闪避", "斗殴", "潜行", "说服", "话术", "魅惑", "恐吓", "偷窃", "神秘学", "克苏鲁神话"]


def load_character_info(character_info):
    st.session_state['current_character_outlook'] = character_info["outlook"] \
        if "outlook" in character_info else None
    st.session_state['current_character_age'] = character_info["age"] \
        if "age" in character_info else None
    st.session_state['current_character_tone'] = character_info["tone"] \
        if "tone" in character_info else None
    st.session_state['current_character_personality'] = character_info["personality"] \
        if "personality" in character_info else None
    st.session_state['current_character_description'] = character_info["description"] \
        if "description" in character_info else None
    st.session_state['current_character_memory'] = character_info["memory"] \
        if "memory" in character_info and character_info["memory"] else None
    if st.session_state['current_character_memory']:
        st.session_state['current_character_memory'] = "\n".join(st.session_state['current_character_memory'])
    st.session_state['current_character_stable_diffusion_tags'] = character_info["stable_diffusion_tags"] \
        if "stable_diffusion_tags" in character_info else None
    if st.session_state['current_character_stable_diffusion_tags']:
        st.session_state['current_character_stable_diffusion_tags'] = \
            ", ".join(st.session_state['current_character_stable_diffusion_tags'])
    st.session_state['current_character_ability'] = character_info["ability"] if "ability" in character_info else {}
    if len(st.session_state['current_character_ability']) < 1:
        for ability_name in ability_names:
            st.session_state['current_character_ability'][ability_name] = None
    st.session_state['current_character_skill'] = character_info["skill"] if "skill" in character_info else {}
    if len(st.session_state['current_character_skill']) < 1:
        for skill_name in skill_names:
            st.session_state['current_character_skill'][skill_name] = None
    df_data = []
    for ability_name, skill_name in zip(ability_names, skill_names):
        df_data.append([ability_name, st.session_state['current_character_ability'][ability_name],
                        skill_name, st.session_state['current_character_skill'][skill_name]])
    df = pd.DataFrame(df_data, columns=["ability", "ability_value", "skill", "skill_value"])
    st.session_state["current_character_ability_and_skill"] = df


if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
    if "game_id" not in st.session_state or st.session_state["game_id"].strip() == "":
        st.session_state["game_id"] = str(uuid.uuid4())
    game_id = st.session_state["game_id"]
    game_resources_root_path = st.session_state["resources_root_path"] + "/" + st.session_state["game_id"]
    st.session_state["game_resources_root_path"] = game_resources_root_path
    if not check_directory(st.session_state["resources_root_path"], st.session_state["game_id"]):
        initial_resources_root_path = st.session_state["initial_resources_root_path"]
        copy_and_rename_directory(initial_resources_root_path, game_resources_root_path)
    if "game" not in st.session_state:
        st.session_state["game"] = get_game(game_id, st.session_state["resources_root_path"])
    game_manager: GameManager = st.session_state["game"]

    with st.container(border=True):
        def on_current_character_selectbox_change():
            if st.session_state["current_character"] != "创建新角色":
                if file_exists(game_resources_root_path + "/characters/player_characters",
                               st.session_state['current_character'] + ".yaml"):
                    with open(game_resources_root_path + "/characters/player_characters/" +
                              st.session_state['current_character'] + ".yaml",
                              "r", encoding="utf-8") as character_yaml:
                        character_info = yaml.load(character_yaml, Loader=yaml.FullLoader)
                        load_character_info(character_info)
                if file_exists(game_resources_root_path + "/characters/non_player_characters",
                               st.session_state['current_character'] + ".yaml"):
                    with open(game_resources_root_path + "/characters/non_player_characters/" +
                              st.session_state['current_character'] + ".yaml",
                              "r", encoding="utf-8") as character_yaml:
                        character_info = yaml.load(character_yaml, Loader=yaml.FullLoader)
                        load_character_info(character_info)
                if file_exists(game_resources_root_path + "/images", st.session_state["current_character"] + ".png"):
                    st.session_state["avatar_image"] = game_resources_root_path + \
                                                       "/images/" + \
                                                       st.session_state["current_character"] + ".png"
                else:
                    if "avatar_image" in st.session_state:
                        del st.session_state["avatar_image"]


        if "character_options" not in st.session_state:
            st.session_state["character_options"] = game_manager.get_selectable_player_characters() + \
                                                    game_manager.get_selectable_non_player_characters() \
                                                    + ["创建新角色"]
        if "current_character_index" not in st.session_state:
            st.session_state["current_character_index"] = None
        current_character_selectbox = st.selectbox(
            "角色",
            st.session_state["character_options"],
            index=st.session_state["current_character_index"],
            placeholder="选择角色",
            label_visibility="collapsed",
            on_change=on_current_character_selectbox_change,
            key="current_character"
        )

        if "current_character" in st.session_state and st.session_state["current_character"] == "创建新角色":
            with st.form("创建新角色"):
                new_character_name = st.text_input("新角色名称", placeholder="新角色名称", label_visibility="collapsed")
                if st.form_submit_button("创建新角色"):
                    st.session_state["character_options"].insert(-1, new_character_name)
                    st.session_state["current_character_index"] = len(st.session_state["character_options"]) - 2
                    if "avatar_image" in st.session_state:
                        del st.session_state["avatar_image"]
                    load_character_info({})
                    st.rerun()

        if "current_character" in st.session_state and st.session_state["current_character"] \
                and st.session_state["current_character"] != "创建新角色":
            character_image_column, character_info_column = st.columns([1, 2])
            with character_image_column:
                with st.container(border=True, height=400):
                    if "avatar_image" in st.session_state:
                        st.image(st.session_state["avatar_image"])
                draw_button_placeholder = st.empty()
                generate_sd_tags_button_placeholder = st.empty()
                if st.button("保存角色形象", use_container_width=True):
                    if isinstance(st.session_state["avatar_image"], Image):
                        st.session_state["avatar_image"].save(game_resources_root_path + "/images/" +
                                                              st.session_state["current_character"] + ".png")
                        st.toast("保存成功。")
            with character_info_column:
                st.write(f"{st.session_state['current_character']}")
                outlook = st.text_input("角色外貌描述",
                                        value=st.session_state['current_character_outlook']
                                        if "current_character_outlook" in st.session_state else None)
                age = st.text_input("年龄",
                                    placeholder="留空表示“未知“",
                                    value=st.session_state['current_character_age']
                                    if "current_character_age" in st.session_state else None)
                tone = st.text_input("语调、说话风格、语癖", placeholder="留空表示“普通”",
                                     value=st.session_state['current_character_tone']
                                     if "current_character_tone" in st.session_state else None)
                personality = st.text_input("人物性格",
                                            value=st.session_state['current_character_personality']
                                            if "current_character_personality" in st.session_state else None)
                description = st.text_input("其他描述", placeholder="留空表示“暂无“",
                                            value=st.session_state['current_character_description']
                                            if "current_character_description" in st.session_state else None)
                tts_name = st.selectbox("TTS配音角色",
                                        options=get_speaker_names(),
                                        index=None,
                                        placeholder="选择一位voicevox配音角色")
                memory = st.text_area("人物记忆",
                                      placeholder="留空表示“暂无“。建议不同的记忆以换行分隔。", height=150,
                                      value=st.session_state['current_character_memory']
                                      if "current_character_memory" in st.session_state else None)
                stable_diffusion_tags = st.text_area(
                    "生成插图使用的 stable diffusion 正面TAG（负面TAG会自行适用，无需写入）",
                    height=100,
                    value=st.session_state['current_character_stable_diffusion_tags']
                    if "current_character_stable_diffusion_tags" in st.session_state else None)
                st.session_state["current_character_ability_and_skill"] = \
                    st.data_editor(st.session_state["current_character_ability_and_skill"],
                                   use_container_width=True,
                                   hide_index=True,
                                   column_config={
                                       "ability": st.column_config.Column(
                                           "能力",
                                           required=True,
                                       ),
                                       "ability_value": st.column_config.Column(
                                           "数值",
                                           required=True,
                                       ),
                                       "skill": st.column_config.Column(
                                           "技能",
                                           required=True,
                                       ),
                                       "skill_value": st.column_config.Column(
                                           "数值",
                                           required=True,
                                       ),
                                   })
        if st.button("保存为玩家角色", use_container_width=True):
            ability_dict = {}
            skill_dict = {}
            ability_and_skill = st.session_state["current_character_ability_and_skill"].to_dict(orient="records")
            for line in ability_and_skill:
                ability_dict[line["ability"]] = line["ability_value"]
                skill_dict[line["skill"]] = line["skill_value"]

            with open(
                    f"{game_resources_root_path}/characters/player_characters/{st.session_state['current_character']}.yaml",
                    'w', encoding="utf-8") as character_yaml:
                yaml.dump({
                    "name": st.session_state['current_character'],
                    "outlook": outlook,
                    "age": age,
                    "tone": tone,
                    "personality": personality,
                    "description": description,
                    "tts_name": tts_name,
                    "memory": memory.split("\n") if memory else [],
                    "stable_diffusion_tags": re.split(r",\s+", stable_diffusion_tags) if stable_diffusion_tags else [],
                    "ability": ability_dict,
                    "skill": skill_dict
                }, character_yaml, allow_unicode=True, sort_keys=False)
            st.toast("保存成功。")
        if st.button("保存为非玩家角色", use_container_width=True):
            ability_dict = {}
            skill_dict = {}
            ability_and_skill = st.session_state["current_character_ability_and_skill"].to_dict(orient="records")
            for line in ability_and_skill:
                ability_dict[line["ability"]] = line["ability_value"]
                skill_dict[line["skill"]] = line["skill_value"]
            with open(
                    f"{game_resources_root_path}/characters/non_player_characters/{st.session_state['current_character']}.yaml",
                    'w', encoding="utf-8") as character_yaml:
                yaml.dump({
                    "name": st.session_state['current_character'],
                    "outlook": outlook,
                    "age": age,
                    "tone": tone,
                    "personality": personality,
                    "description": description,
                    "tts_name": tts_name,
                    "memory": memory.split("\n") if memory else [],
                    "stable_diffusion_tags": re.split(r",\s+", stable_diffusion_tags) if stable_diffusion_tags else [],
                    "ability": ability_dict,
                    "skill": skill_dict
                }, character_yaml, allow_unicode=True, sort_keys=False)
            st.toast("保存成功。")

        if st.button("返回路由页面", use_container_width=True):
            st.switch_page("streamlit_app.py")
        if "current_character" in st.session_state and st.session_state["current_character"] \
                and st.session_state["current_character"] != "创建新角色":
            if draw_button_placeholder.button("生成人物形象插画", use_container_width=True):
                # png_save_path = game_resources_root_path + f"/images/{st.session_state['current_character']}.png"
                st.session_state["avatar_image"] = draw(stable_diffusion_tags)
                st.rerun()
            if generate_sd_tags_button_placeholder.button("根据已有描述信息生成 stable diffusion 正面TAG",
                                                          use_container_width=True):
                if not outlook:
                    st.toast("必须至少填写了外貌描述才能使用此功能")
                else:
                    st.session_state['current_character_stable_diffusion_tags'] = ",".join(generate_character_tags(outlook))
                    st.rerun()




else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
