import gradio as gr

from outdated.keeper_layout import define_keeper_layout
from outdated.player_layout import generate_player_layout
from scene.SceneManager import SceneManager

config_root_path = "../files"
scene_manager = SceneManager(config_root_path)

with gr.Blocks() as app:
    generate_player_layout(config_root_path, scene_manager)

    define_keeper_layout(config_root_path, scene_manager)

    with gr.Tab(label="即时插图"):
        gr.Image(type='filepath', label="插图", value=scene_manager.get_illustration_path, every=1)

app.launch()
