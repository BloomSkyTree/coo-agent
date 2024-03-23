import re
import time

from agentscope.agents import UserAgent
from loguru import logger
from scene.SceneManager import SceneManager

if __name__ == '__main__':
    keeper_agent = UserAgent(name="KP")
    scene_manager = SceneManager("files")
    # keeper_agent.reset_audience([kp_command_router_agent])
    # player_agent.reset_audience([pl_command_router_agent])
    while True:
        time.sleep(0.5)
        # keeper_command = keeper_agent()
        # router_result = re.split("[,，、]", kp_command_router_agent()["content"].strip())
        # for router in router_result:
        #
        #     try_eval_message(agents_router[router], keeper_command)
        auth = input("发言者身份：")
        if auth == "KP":
            keeper_command = keeper_agent()
            # router_result = re.split("[,，、]", kp_command_router_agent()["content"].strip())
            # for router in router_result:
            #     try_eval_message(agents_router[router.strip()], keeper_command)
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
                # router_result = re.split("[,，、]", pl_command_router_agent()["content"].strip())
                # for router in router_result:
                #     try_eval_message(agents_router[router], player_input)
            except Exception as e:
                logger.exception(e)
