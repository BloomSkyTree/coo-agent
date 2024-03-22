import re
import time
from loguru import logger
from agents.singleton import kp_command_router_agent, keeper_agent, agents_router
from scene.SceneManager import SceneManager
def try_eval_message(agent, command):
    try:
        python_code = agent(command)["content"]
        eval(python_code)
    except Exception as e:
        logger.error("尝试执行以下python代码失败：{python_code}")
        try_eval_message(agent, command)


if __name__ == '__main__':
    scene_manager = SceneManager("files")
    keeper_agent.reset_audience([kp_command_router_agent])
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
            router_result = re.split("[,，、]", kp_command_router_agent()["content"].strip())
            for router in router_result:
                try_eval_message(agents_router[router.strip()], keeper_command)
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
