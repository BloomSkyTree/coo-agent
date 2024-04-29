import uuid
import streamlit as st
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
        def on_current_scene_selectbox_change():
            if st.session_state["current_character"] != "创建新角色":
                pass
                # game_manager.enter_scene(scene_name=st.session_state["current_character"])

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
            on_change=on_current_scene_selectbox_change,
            key="current_character"
        )

        if "current_character" in st.session_state and st.session_state["current_character"] == "创建新角色":
            with st.form("创建新角色"):
                new_character_name = st.text_input("新场景名称", placeholder="新场景名称", label_visibility="collapsed")
                if st.form_submit_button("创建新角色"):
                    st.session_state["character_options"].insert(-1, new_character_name)
                    st.session_state["current_character_index"] = len(st.session_state["character_options"]) - 2
                    if "avatar_image" in st.session_state:
                        del st.session_state["avatar_image"]
                    st.rerun()

        if "current_character" in st.session_state and st.session_state["current_character"]:
            character_image_column, character_info_column = st.columns([1, 2])
            with character_image_column:
                with st.container(border=True, height=400):
                    if "avatar_image" in st.session_state:
                        st.image(st.session_state["avatar_image"])
                if st.button("生成人物形象插画", use_container_width=True):
                    pass
                if st.button("根据已有描述信息生成 stable diffusion 正面TAG", use_container_width=True):
                    pass
            with character_info_column:
                st.write(f"{st.session_state['current_character']}")
                outlook = st.text_input("角色外貌描述")
                age = st.text_input("年龄", placeholder="留空表示“未知“")
                tone = st.text_input("语调、说话风格、语癖", placeholder="留空表示“普通”")
                personality = st.text_input("人物性格")
                description = st.text_input("其他描述", placeholder="留空表示“暂无“")
                memory = st.text_area("人物记忆", placeholder="留空表示“暂无“。建议不同的记忆以换行分隔。", height=150)
                stable_diffusion_tags = st.text_area("生成插图使用的 stable diffusion 正面TAG（负面TAG会自行适用，无需写入）",
                                                     height=150)
        if st.button("保存为玩家角色", use_container_width=True):
            pass
        if st.button("保存为非玩家角色", use_container_width=True):
            pass
        if st.button("返回路由页面", use_container_width=True):
            st.switch_page("streamlit_app.py")


else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
