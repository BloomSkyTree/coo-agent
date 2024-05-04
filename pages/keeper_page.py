import time
import uuid
import pandas as pd
import streamlit as st
from PIL import Image
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

    with st.container(border=True):
        scene_select_column, scene_op_column = st.columns([7, 1])
        with scene_select_column:
            def on_current_scene_selectbox_change():
                get_game(game_id).enter_scene(scene_name=st.session_state["current_scene"])


            current_scene_selectbox = st.selectbox(
                "场景",
                get_game(game_id).get_selectable_scenes(),
                index=None,
                placeholder="选择场景",
                label_visibility="collapsed",
                on_change=on_current_scene_selectbox_change,
                key="current_scene"
            )
        with scene_op_column:
            if st.button("描绘场景", use_container_width=True):
                get_game(game_id).draw_a_panorama()
                st.rerun()

    main_row = st.columns([3, 7])
    with main_row[0]:
        with st.container(border=True, height=360):
            if "current_npc" in st.session_state and st.session_state["current_npc"]:
                st.image(game_resources_root_path + f"/images/{st.session_state['current_npc']}.png")
        if st.button("描绘外貌", use_container_width=True):
            get_game(game_id).character_outlook(st.session_state["current_npc"])
        df_data = get_game(game_id).get_selectable_character_ability_and_skill(st.session_state["current_npc"]) \
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
        story_container_placeholder.container(border=True, height=360)
        npc_rp_column, aside_column = st.columns([1, 1])
        with npc_rp_column:
            with st.container(border=True):
                current_npc = st.selectbox(
                    "NPC",
                    get_game(game_id).get_selectable_non_player_characters(),
                    index=None,
                    placeholder="选择NPC",
                    label_visibility="collapsed",
                    key="current_npc"
                )
                with st.form("角色扮演", clear_on_submit=True, border=False):
                    rp_command = st.text_input("角色扮演命令",
                                               placeholder="角色扮演命令",
                                               label_visibility="collapsed")
                    if st.form_submit_button("进行角色扮演", use_container_width=True):
                        if rp_command and "current_npc" in st.session_state and st.session_state["current_npc"]:
                            get_game(game_id).character_act(st.session_state["current_npc"], rp_command)
        with aside_column:
            with st.container(border=True):
                with st.form("旁白", clear_on_submit=True, border=False):
                    aside_content = st.text_input("旁白",
                                                  placeholder="旁白",
                                                  label_visibility="collapsed")
                    if st.form_submit_button("发送旁白", use_container_width=True):
                        logger.info(f"发送旁白：{aside_content}")
                        get_game(game_id).submit_aside(aside_content)
                if st.button("即时情节插画（取决于SD API端点性能，耗时较长）", use_container_width=True):
                    get_game(game_id).illustrate()
        if st.button("保存游戏", use_container_width=True):
            get_game(game_id).save()
            st.toast("保存完成。")
        if st.button("重载游戏（若未保存，会丢失进度）", use_container_width=True):
            get_game(game_id, reload=True)
            st.rerun()
            st.toast("刷新完成。")
        if st.button("退出游戏（退出前，请记得保存，否则会丢失进度）", use_container_width=True):
            st.switch_page("streamlit_app.py")
    while True:
        if len(st.session_state["kp_messages"]) < len(st.session_state["game"].get_script()):
            with story_container_placeholder.container(border=True, height=360):
                st.text(f"Story: {st.session_state['game_id']}")
                for message in st.session_state["game"].get_script():
                    message_content = message.content
                    if message_content.endswith("png"):
                        message_content = Image.open(message_content)

                    if file_exists(game_resources_root_path + "/images", f"{message.role}.png"):
                        chat_message = st.chat_message(message.role,
                                                       avatar=game_resources_root_path + f"/images/{message.role}.png")
                    else:
                        chat_message = st.chat_message(message.role)
                    with chat_message:
                        if isinstance(message_content, str) and message_content.endswith(".wav"):
                            st.audio(message_content)
                        elif isinstance(message_content, str):
                            st.write(message_content)
                        elif isinstance(message_content, Image.Image):
                            st.image(message_content, width=300)

                st.session_state["kp_messages"] = st.session_state["game"].get_script()
        time.sleep(1)




else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
