import re
import time

from agentscope.agents import UserAgent
from loguru import logger
from scene.SceneManager import SceneManager

if __name__ == '__main__':
    keeper_agent = UserAgent(name="KP")
    scene_manager = SceneManager("../files")
    while True:
        time.sleep(0.5)
        auth = input("发言者身份：")
        if auth == "KP":
            keeper_command = keeper_agent()
            python_code = scene_manager(keeper_command)["content"]
            if "`" in python_code:
                python_code = "\n".join([line for line in python_code.split("\n") if not line.startswith("`")])
            try:
                exec(python_code)
            except Exception as e:
                logger.exception(e)
                logger.error(f"尝试执行以下python代码失败：{python_code}")
        elif auth == "eval":
            code = input("输入执行的代码：")
            eval(code)
        else:
            try:
                player_input = input(f"{auth}：")
                scene_manager.player_role_play(auth, player_input)
            except Exception as e:
                logger.exception(e)
