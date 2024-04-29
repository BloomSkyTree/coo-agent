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
            if st.session_state["current_scene"] != "创建新场景":
                game_manager.enter_scene(scene_name=st.session_state["current_scene"])

        if "scene_options" not in st.session_state:
            st.session_state["scene_options"] = game_manager.get_selectable_scenes() + ["创建新场景"]
        if "current_scene_index" not in st.session_state:
            st.session_state["current_scene_index"] = None
        current_scene_selectbox = st.selectbox(
            "场景",
            st.session_state["scene_options"],
            index=st.session_state["current_scene_index"],
            placeholder="选择场景",
            label_visibility="collapsed",
            on_change=on_current_scene_selectbox_change,
            key="current_scene"
        )

        if "current_scene" in st.session_state and st.session_state["current_scene"] == "创建新场景":
            with st.form("创建新场景"):
                new_scene_name = st.text_input("新场景名称", placeholder="新场景名称", label_visibility="collapsed")
                if st.form_submit_button("创建新场景"):
                    st.session_state["scene_options"].insert(-1, new_scene_name)
                    st.session_state["current_scene_index"] = len(st.session_state["scene_options"]) - 2
                    if "scene_image" in st.session_state:
                        del st.session_state["scene_image"]
                    st.rerun()

        if "current_scene" in st.session_state:
            scene_image, scene_info_column = st.columns([1, 2])
            with scene_image:
                with st.container(border=True, height=400):
                    if "scene_image" in st.session_state:
                        st.image(st.session_state["scene_image"])
                if st.button("生成场景插画", use_container_width=True):
                    pass
                if st.button("根据已有描述信息生成 stable diffusion 正面TAG", use_container_width=True):
                    pass
            with scene_info_column:
                st.write(f"{st.session_state['current_scene']}")
                era = st.text_input("场景年代", placeholder="留空表示“未知“")
                position = st.text_input("场景所处位置", placeholder="留空表示“未知“")
                description = st.text_input("场景描述", placeholder="留空表示“暂无“")
                memory = st.text_area("场景记忆", placeholder="留空表示“暂无“。建议不同的记忆以换行分隔。", height=150)
                stable_diffusion_tags = st.text_area("生成插图使用的 stable diffusion 正面TAG（负面TAG会自行适用，无需写入）",
                                                     height=150)
        if st.button("保存场景", use_container_width=True):
            pass
        if st.button("返回路由页面", use_container_width=True):
            st.switch_page("streamlit_app.py")


else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
