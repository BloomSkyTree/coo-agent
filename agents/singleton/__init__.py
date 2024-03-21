from agentscope.agents import UserAgent

from agents.KeeperControlledAgent import KeeperControlledAgent

kp_command_router_agent = KeeperControlledAgent(
    name="KP命令路由",
    sys_prompt="你是指令的传达者。根据给出的指令，判断指令需要传达给以下哪些对象。"
               "注意：指令可能影响多个对象。"
               "以下是可能成为指令目标的对象：\n"
               "场景管理器：接受与周边环境、物件、景色有关的指令。\n"
               "人物管理器：只接受与登场人物的言语、动作有关的指令。\n"
               "战斗管理器：只接受战斗轮开始的指令。\n"
               "追逐管理器：只接受追逐轮开始的指令。\n"
               "检定管理器：接受进行检定相关的指令。除了直接声明检定外，“过一个XX”也视作是检定的声明。"
               "此外，尝试进行一个未必成功（且有难度）的行动也与检定管理器有关。\n"
               "以顿号为间隔，回答所有接受指令的对象。",
    model_config_name="qwen-max",
    use_memory=True
)

keeper_agent = UserAgent(name="指令")
player_agent = UserAgent(name="阿特拉斯")
scene_manager_agent = KeeperControlledAgent(
    name="场景管理器",
    sys_prompt="你是一个智能场景管理器。根据接受到的命令类型不同，你需要进行不同的python代码执行。\n"
               "进入场景时，调用scene_manager.enter_scene(scene_name: str)方法。"
               "需要对场景进行描绘时，调用scene_manager.draw_a_panorama()方法。\n"
               "当命令会对场景本身或场景中的物件造成持久的影响时：scene_manager.generate_scene_memory(full_command: str)\n"
               "当命令是对场景进行归档、保存或存档时：scene_manager.save()\n"
               "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
               "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
    model_config_name="qwen-max",
    use_memory=True
)
character_manager_agent = KeeperControlledAgent(
    name="人物管理器",
    sys_prompt="你是一个智能人物管理器，与scene_manager一同协作运行。根据接受到的描述类型不同，你需要进行不同的python代码执行。\n"
               "当描述是某一个人物“登场”时，调用scene_manager.character_enter(character_name:str)方法。\n"
               "当需要对人物外貌进行描述时，调用scene_manager.character_outlook(character_name:str)方法。\n"
               "当描述是一个人物在进行某一行动（登场不计入在内）时，调用scene_manager.character_act(character_name:str, act: str)方法，其中act字段应包含原始指令中对动作的详细描述。\n"
               "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
               "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
    model_config_name="qwen-max",
    use_memory=True
)

check_manager_agent = KeeperControlledAgent(
    name="检定管理器",
    sys_prompt="你是一个COC智能检定管理器。根据接受到的输入类型不同，你需要进行不同的python代码执行。\n"
               "当输入是某一个人物在进行某一行动时，调用determine_check(act:str)方法。\n"
               "当输入是要求某一人物进行检定（有时会被表述为“过一个……”）时，调用do_check(character_name:str, check: str, check_difficulty)方法。\n"
               "如果描述中同时包含行动和发言，则上述代码都需要执行。"
               "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
               "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
    model_config_name="qwen-max",
    use_memory=True
)

agents_router = {
    "场景管理器": scene_manager_agent,
    "人物管理器": character_manager_agent,
    "检定管理器": check_manager_agent
}

# pl_command_router_agent = KeeperControlledAgent(
#     name="PL命令路由",
#     sys_prompt="你是角色扮演指令的传达者。根据给出的角色扮演指令，判断指令需要传达给以下哪些对象。"
#                "注意：指令可能影响多个对象。"
#                "以下是可能成为指令目标的对象：\n"
#                "人物管理器：只接受与登场人物的言语、动作有关的指令。\n"
#                "检定管理器：接受进行检定相关的指令。除了直接声明检定外，“过一个XX”也视作是检定的声明。"
#                "此外，尝试进行一个未必成功（且有难度）的行动也与检定管理器有关。\n"
#                "以顿号为间隔，回答所有接受指令的对象。",
#     model_config_name="qwen-max",
#     use_memory=True
# )
