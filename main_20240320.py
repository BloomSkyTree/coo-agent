import agentscope
from agentscope import msghub

from agents.KeeperControlledAgent import KeeperControlledAgent
from agents.singleton import command_router_agent, keeper_agent, player_agent, agents_router
from scripts.ScriptManager import ScriptManager
model_configs = [
    {
        "config_name": "qwen-max",
        "model_type": "dashscope_chat",
        "model_name": "qwen-max",
        "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "api_key": "sk-d1c122e76c8a4d11b78b3734e48960c6",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "sk-d1c122e76c8a4d11b78b3734e48960c6"
        },
        "messages_key": "input"
    }
]
agentscope.init(model_configs=model_configs)
if __name__ == '__main__':
    keeper_agent.reset_audience([command_router_agent])
    while True:
        auth = input("发言者身份：")
        if auth == "KP":
            keeper_command = keeper_agent()
            router_result = command_router_agent()["content"].strip().split("、")
            for router in router_result:
                agents_router[router](keeper_command)
        else:
            player_input = player_agent()





