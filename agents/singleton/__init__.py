from agentscope.agents import UserAgent

from agents.KeeperControlledAgent import KeeperControlledAgent

character_outlook_agent = KeeperControlledAgent(
    name="character outlook agent",
    sys_prompt="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、神态进行描写。"
               "注意，你描述的信息不应超出被提供的信息的范围，且不允许进行心理描写。"
               "除非明确要求，否则不允许有褒贬之意。尽量简短、白描。"
               "以“有一位”开头，开始你的叙述。",
    model_config_name="qwen-max",
    use_memory=True
)

command_router_agent = KeeperControlledAgent(
    name="命令路由",
    sys_prompt="你是指令的传达者。根据给出的指令，判断指令需要传达给以下哪些对象。"
               "注意：指令可能影响多个对象。"
               "以下是可能成为指令目标的对象："
               "场景管理器：接受与环境、物件有关的指令。"
               "人物管理器：只接受与登场人物的言语、动作有关的指令。"
               "战斗管理器：只接受战斗轮开始的指令。"
               "追逐管理器：只接受追逐轮开始的指令。"
               "以、为间隔，回答所有接受指令的对象。",
    model_config_name="qwen-max",
    use_memory=True
)

keeper_agent = UserAgent(name="指令")
player_agent = UserAgent(name="阿特拉斯")
scene_manager_agent = KeeperControlledAgent(
    name="场景管理器",
    sys_prompt="你是一个智能场景管理器。根据接受到的命令类型不同，你需要进行不同的python代码执行。\n"
               "当进入场景，或者需要对场景进行描绘时，调用draw_a_panorama()方法。\n"
               "当命令会对场景本身或场景中的物件造成持久的影响时：generate_scene_memory(full_command: str)\n"
               "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。\n"
               "注意：你只能回答python代码，不能回答其他多余的内容。",
    model_config_name="qwen-max",
    use_memory=True
)
character_manager_agent = KeeperControlledAgent(
    name="人物管理器",
    sys_prompt="你是一个智能人物管理器。根据接受到的描述类型不同，你需要进行不同的python代码执行。\n"
               "当描述是某一个人物“登场”时，调用character_enter(character_name:str)方法。\n"
               "当描述是一个人物在进行某一行动（登场不计入在内）时，调用character_act(character_name:str, act: str)方法。\n"
               "当描述是一个人物在进行发言时：调用character_say(character_name:str, content: str, expression: str)，"
               "其中content为人物的发言内容，expression是该人物的神态描述。\n"
               "如果描述中同时包含行动和发言，则上述代码都需要执行。"
               "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。\n"
               "注意：你只能回答python代码，不能回答其他多余的内容。",
    model_config_name="qwen-max",
    use_memory=True
)

agents_router = {
    "场景管理器": scene_manager_agent,
    "人物管理器": character_manager_agent
}
