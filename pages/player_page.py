import numpy as np
import pandas as pd
import streamlit as st

if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
    # with st.container(border=True):
    #     row_1 = st.columns([8, 2])
    #     with row_1[0]:
    #         with st.container(border=True):
    #             st.text(f"{st.session_state['nickname']}，您正在进行的游戏ID为：{st.session_state['game_id']}")
    #
    #     with row_1[1]:
    #         if st.button("退出游戏", use_container_width=True):
    #             st.switch_page("streamlit_app.py")

    main_row = st.columns([1, 1])
    with main_row[0]:
        with st.container(border=True, height=360):
            st.image("files/images/阿特拉斯.png")
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
        with st.container(border=True):
            st.text_area(f"Story: {st.session_state['game_id']}", height=300, disabled=True)
        with st.container(border=True):
            act = st.text_input("行动", placeholder="行动", label_visibility="collapsed")
            say = st.text_input("发言", placeholder="发言", label_visibility="collapsed")
            if st.button("提交", use_container_width=True):
                pass
            if st.button("退出游戏", use_container_width=True):
                st.switch_page("streamlit_app.py")


else:
    st.text(f"您尚未登录，或登录信息已失效。请返回登录。")
    if st.button("返回登录界面"):
        st.switch_page("streamlit_app.py")
