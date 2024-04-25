import math
import uuid

import numpy as np
import pandas as pd
import streamlit as st
from loguru import logger

from game import get_game
from game.GameManager import GameManager
from utils.file_system_utils import check_directory, copy_and_rename_directory, file_exists

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
        row_1 = st.columns([1, 1])
        with row_1[0]:
            st.session_state["current_npc"] = st.selectbox(
                "NPC",
                ["爱丽丝"],
                index=None,
                placeholder="选择NPC",
                label_visibility="collapsed"
            )

        with row_1[1]:
            def on_current_scene_selectbox_change():
                game_manager.enter_scene(scene_name=st.session_state["current_scene"])

            current_scene_selectbox = st.selectbox(
                "场景",
                game_manager.get_selectable_scenes(),
                index=None,
                placeholder="选择场景",
                label_visibility="collapsed",
                on_change=on_current_scene_selectbox_change,
                key="current_scene"
            )

    main_row = st.columns([1, 1])
    with main_row[0]:
        avatar_column, op_column = st.columns([3, 1])
        with avatar_column:
            with st.container(border=True, height=360):
                if "current_npc" in st.session_state and st.session_state["current_npc"]:
                    st.image(f"files/images/{st.session_state['current_npc']}.png")
        with op_column:
            with st.container(border=True, height=360):
                rp_command = st.text_area("角色扮演命令",
                                          placeholder="角色扮演命令",
                                          height=100,
                                          label_visibility="collapsed")
                if st.button("进行角色扮演", use_container_width=True):
                    pass
                check_name = st.text_input("检定", placeholder="检定名", label_visibility="collapsed")
                if st.button("进行检定", use_container_width=True):
                    pass
                if st.button("描绘外貌", use_container_width=True):
                    game_manager.character_outlook(st.session_state["current_npc"])
        df = pd.DataFrame(np.random.randn(10, 2), columns=["name", "value"])
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={
            "name": st.column_config.Column(
                "能力/技能",
                width="small",
                required=True,
            ),
            "value": st.column_config.Column(
                "数值",
                width="large",
                required=True,
            ),
        })
    with main_row[1]:
        with st.container(border=True, height=350):
            st.text(f"Story: {st.session_state['game_id']}")
            for message in st.session_state["game"].get_script():
                height = math.ceil(len(message.content) / 34) * 32
                height = height if height > 80 else 80
                with st.container(border=True, height=height):
                    chat_avatar_column, chat_content_column = st.columns([1, 10])
                    with chat_avatar_column:
                        character_name = message.role
                        if file_exists(game_resources_root_path + "/images", f"{character_name}.png"):
                            st.image("files/images/爱丽丝.png", width=50)
                        else:
                            st.text(character_name)
                    with chat_content_column:
                        st.write(message.content)
        with st.container(border=True):
            act = st.text_input("行动", placeholder="行动", label_visibility="collapsed")
            say = st.text_input("发言", placeholder="发言", label_visibility="collapsed")
            if st.button("提交", use_container_width=True):
                pass
            if st.button("描绘场景", use_container_width=True):
                game_manager.draw_a_panorama()
                st.rerun()
            if st.button("退出游戏", use_container_width=True):
                st.switch_page("streamlit_app.py")


else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
