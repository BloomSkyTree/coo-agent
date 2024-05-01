import math
import time

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from loguru import logger

from game import get_game, GameManager
from utils.file_system_utils import check_directory, file_exists

if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
    if "game_id" not in st.session_state or st.session_state["game_id"].strip() == "" or not \
            check_directory(st.session_state["resources_root_path"], st.session_state["game_id"]):
        st.text("未提供合法游戏ID，或该游戏已被删除。")
        if st.button("返回键入游戏ID界面"):
            st.switch_page("streamlit_app.py")
    else:
        game_id = st.session_state["game_id"]
        game_resources_root_path = st.session_state["resources_root_path"] + "/" + st.session_state["game_id"]
        st.session_state["game_resources_root_path"] = game_resources_root_path
        if "game" not in st.session_state:
            st.session_state["game"] = get_game(game_id, st.session_state["resources_root_path"])

        main_row = st.columns([4, 7])
        with main_row[0]:
            with st.container(border=True, height=300):
                if "player_name" in st.session_state:
                    st.image(f"{game_resources_root_path}/images/{st.session_state['player_name']}.png")
            df_data = get_game(game_id).get_selectable_character_ability_and_skill(st.session_state["player_name"]) \
                if "player_name" in st.session_state else []
            df = pd.DataFrame(df_data, columns=["name", "value"])
            st.dataframe(df, use_container_width=True, hide_index=True, column_config={
                "name": st.column_config.Column(
                    "能力/技能",
                    # width="medium",
                    required=True,
                ),
                "value": st.column_config.Column(
                    "数值",
                    # width="large",
                    required=True,
                ),
            })
        with main_row[1]:
            st.session_state["pl_messages"] = []
            with st.container(border=True):
                st.text(f"Story: {st.session_state['game_id']}")
            story_container_placeholder = st.empty()

            with st.container(border=True):
                player_name = st.selectbox(
                    "玩家角色",
                    get_game(game_id).get_selectable_player_characters(),
                    index=None,
                    placeholder="选择角色",
                    label_visibility="collapsed",
                    key="player_name"
                )
                with st.form("Role Play", clear_on_submit=True):
                    act = st.text_input("行动", placeholder="行动", label_visibility="collapsed", key="player_act")
                    say = st.text_input("发言", placeholder="发言", label_visibility="collapsed", key="play_say")
                    if st.form_submit_button("提交", use_container_width=True):
                        role_play = ""
                        if act:
                            role_play += f"（{act}）"
                        if say:
                            role_play += f"”{say}“"
                        if role_play:
                            get_game(game_id).player_role_play(player_name, role_play)
                            st.rerun()
                if st.button("退出游戏", use_container_width=True):
                    st.switch_page("streamlit_app.py")

        while True:
            if len(st.session_state["pl_messages"]) < len(st.session_state["game"].get_script()):
                with story_container_placeholder.container(border=True, height=350):
                    for message in st.session_state["game"].get_script():
                        message_content = message.content
                        if message_content.startswith(game_resources_root_path):
                            message_content = Image.open(message_content)

                        if file_exists(game_resources_root_path + "/images", f"{message.role}.png"):
                            chat_message = st.chat_message(message.role,
                                                           avatar=game_resources_root_path + f"/images/{message.role}.png")
                        else:
                            chat_message = st.chat_message(message.role)
                        with chat_message:
                            if isinstance(message_content, str):
                                st.write(message_content)
                            elif isinstance(message_content, Image.Image):
                                st.image(message_content, width=300)
                    st.session_state["pl_messages"] = st.session_state["game"].get_script()

            time.sleep(1)

else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
