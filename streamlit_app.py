import streamlit as st
from loguru import logger

st.set_page_config(layout="wide")
st.session_state["resources_root_path"] = "files"
st.session_state["initial_resources_root_path"] = "files/resources"

if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
    if st.session_state["authentication_status"]:
        st.text(f"欢迎您，{st.session_state['nickname']}")
        if "game_id" in st.session_state:
            text_input_game_id = st.text_input("请输入游戏ID，访问已创建的游戏（置空以创建新游戏）",
                                               value=st.session_state["game_id"])
        else:
            text_input_game_id = st.text_input("请输入游戏ID，访问已创建的游戏（置空以创建新游戏）")
        if st.button("以玩家身份进入游戏", use_container_width=True):
            st.session_state["game_id"] = text_input_game_id
            st.switch_page("pages/player_page.py")

        if st.button("以主持人身份进入游戏", use_container_width=True):
            st.session_state["game_id"] = text_input_game_id
            st.switch_page("pages/keeper_page.py")
        if st.button("进入人物编辑器", use_container_width=True):
            st.session_state["game_id"] = text_input_game_id
            st.switch_page("pages/character_edit_page.py")
        if st.button("进入场景编辑器", use_container_width=True):
            st.session_state["game_id"] = text_input_game_id
            st.switch_page("pages/scene_edit_page.py")
        if st.button("注销", type="primary", use_container_width=True):
            del st.session_state["authentication_status"]

else:
    if "authentication_status" in st.session_state and not st.session_state["authentication_status"]:
        st.error("用户名或密码错误，请重新登录。")
    username_input = st.text_input("用户名")
    password_input = st.text_input("密码")


    def login(username, password):
        if username.lower() == "yuka" and password.lower() == "test":
            st.session_state["authentication_status"] = True
            st.session_state["nickname"] = "Yuka"
        else:
            st.session_state["authentication_status"] = False
        logger.debug(f"username: {username}, password: {password}")


    st.button("登录", on_click=login, args=[username_input, password_input], use_container_width=True)
