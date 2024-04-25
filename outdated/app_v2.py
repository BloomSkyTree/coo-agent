import os
import shutil
import uuid

import gradio as gr

from outdated.keeper_layout import define_keeper_layout
from outdated.player_layout import generate_player_layout
from scene.SceneManager import SceneManager

sessions_root_path = "../sessions"
session_id_to_component = {}


# 假设这是你的主应用界面
def define_main_app(session_id):
    session_path = sessions_root_path + f"/{session_id}"

    scene_manager = SceneManager(session_path)
    with gr.Blocks() as main_app:
        generate_player_layout(session_path, scene_manager)

        define_keeper_layout(session_path, scene_manager)

        with gr.Tab(label="即时插图"):
            gr.Image(type='filepath', label="插图", value=scene_manager.get_illustration_path, every=1)

    return main_app


# 这个函数用于验证会话ID的有效性
def is_valid_session_id(session_id):
    # 这里检查session_id是否有效
    if os.path.exists(sessions_root_path + f"/{session_id}"):
        return True
    return False


with gr.Blocks() as app:
    main_app = gr.Blocks()
    session_id_input = gr.Textbox(label="Enter or create a session ID")
    with gr.Row():
        create_button = gr.Button("创建新的Session ID")
        submit_button = gr.Button("提交Session ID")


    @create_button.click()
    def create_new_session():
        # 复制resources文件夹的内容到self._config_root_path
        resources_path = os.path.join(os.getcwd(), '../files/resources')
        session_id = uuid.uuid4()
        shutil.copytree(resources_path, sessions_root_path + f"/{session_id}")
        gr.Info(f"已创建新的Session ID：{session_id}")
        # session_id_to_component[session_id] = define_main_app(session_id)
        with main_app:
            define_main_app(session_id)


    @submit_button.click(inputs=[session_id_input])
    def submit_session_id(session_id):
        if is_valid_session_id(session_id):
            gr.Info(f"合法的session id：{session_id}，将为您加载游戏...")
            if session_id not in session_id_to_component:
                session_id_to_component[session_id] = define_main_app(session_id)
            session_id_to_component[session_id].render()
        else:
            gr.Info(f"session id：{session_id}不存在，无法加载游戏。")

app.launch()
