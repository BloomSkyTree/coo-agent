import math
import threading
import time
import uuid
import numpy as np
import pandas as pd
import streamlit as st
from loguru import logger
from streamlit.runtime.scriptrunner import add_script_run_ctx
from game import get_game
from game.GameManager import GameManager
from utils.file_system_utils import check_directory, copy_and_rename_directory, file_exists

if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
    if "game_id" not in st.session_state or st.session_state["game_id"].strip() == "":
        st.session_state["game_id"] = str(uuid.uuid4())
    game_id = st.session_state["game_id"]
    game_resources_root_path = st.session_state["resources_root_path"] + "/" + st.session_state["game_id"]
    game_sync_cache_path = st.session_state["resources_root_path"] + "/" + st.session_state["game_id"] + "/cache"
    st.session_state["game_resources_root_path"] = game_resources_root_path
    if not check_directory(st.session_state["resources_root_path"], st.session_state["game_id"]):
        initial_resources_root_path = st.session_state["initial_resources_root_path"]
        copy_and_rename_directory(initial_resources_root_path, game_resources_root_path)
    if "game" not in st.session_state:
        st.session_state["game"] = get_game(game_id, st.session_state["resources_root_path"])
    game_manager: GameManager = st.session_state["game"]

    with st.container(border=True):
        scene_select_column, scene_op_column = st.columns([7, 1])
        with scene_select_column:
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
        with scene_op_column:
            if st.button("描绘场景", use_container_width=True):
                game_manager.draw_a_panorama()
                st.rerun()

    main_row = st.columns([3, 7])
    with main_row[0]:
        with st.container(border=True, height=360):
            if "current_npc" in st.session_state and st.session_state["current_npc"]:
                st.image(f"files/images/{st.session_state['current_npc']}.png")
        if st.button("描绘外貌", use_container_width=True):
            game_manager.character_outlook(st.session_state["current_npc"])
        df_data = game_manager.get_selectable_character_ability_and_skill(st.session_state["current_npc"]) \
            if "current_npc" in st.session_state else []
        df = pd.DataFrame(df_data, columns=["name", "value"])
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={
            "name": st.column_config.Column(
                "能力/技能",
                required=True,
            ),
            "value": st.column_config.Column(
                "数值",
                required=True,
            ),
        })
    with main_row[1]:
        st.session_state["kp_messages"] = []
        story_container_placeholder = st.empty()
        with st.container(border=True):
            # npc_select_column, npc_command_column = st.columns([2, 8])
            # with npc_select_column:
            current_npc = st.selectbox(
                "NPC",
                game_manager.get_selectable_non_player_characters(),
                index=None,
                placeholder="选择NPC",
                label_visibility="collapsed",
                key="current_npc"
            )
            # with npc_command_column:
            with st.form("Role Play", clear_on_submit=True, border=False):
                rp_command = st.text_input("角色扮演命令",
                                           placeholder="角色扮演命令",
                                           label_visibility="collapsed")
                if st.form_submit_button("进行角色扮演", use_container_width=True):
                    if rp_command and "current_npc" in st.session_state and st.session_state["current_npc"]:
                        game_manager.character_act(st.session_state["current_npc"], rp_command)

        if st.button("退出游戏", use_container_width=True):
            st.switch_page("streamlit_app.py")
    while True:
        if len(st.session_state["kp_messages"]) < len(st.session_state["game"].get_script()):
            with story_container_placeholder.container(border=True, height=360):
                st.text(f"Story: {st.session_state['game_id']}")
                for message in st.session_state["game"].get_script():
                    if file_exists(game_resources_root_path + "/images", f"{message.role}.png"):
                        st.chat_message(message.role, avatar=game_resources_root_path + f"/images/{message.role}.png")\
                            .write(message.content)
                    else:
                        st.chat_message(message.role).write(message.content)
                st.session_state["kp_messages"] = st.session_state["game"].get_script()
        time.sleep(1)




else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
