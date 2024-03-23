import agentscope
from agentscope.agents import UserAgent

from agents.KeeperControlledAgent import KeeperControlledAgent
from characters.NonPlayerCharacter import NonPlayerCharacter
from scene.Scene import Scene

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
    s = Scene("二十一世纪初", "上海市立图书馆",
              "中央有天井，由于是周末，人不多")

    npc = NonPlayerCharacter(
        name="安理",
        outlook="少女，黑长直，样貌一般，戴眼镜",
        age="十七八岁",
        tone="没干劲，语言礼貌但却简略，惜字如金，话音拖长",
        personality="寡淡",
        description="氛围阴郁，正推着很沉的推车，上面放满了书。倾向于只给出最简单的帮助，除非对对方有好感。",
        model_config_name="qwen-max"
    )
    s.add_non_player_character(npc)

    # panorama_agent = KeeperControlledAgent(
    #     name="scene agent",
    #     sys_prompt="你是一个画面描述助手。根据提供的场景信息和额外提示词，你需要为其生成洛夫·克拉夫特风格的"
    #                "画面描述。但是，别提到洛夫·克拉夫特。"
    #                "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
    #                "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
    #                "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。",
    #     model_config_name="qwen-max",
    #     use_memory=True
    # )
    # panorama_agent(s.get_panorama_prompt())

    character_outlook_agent = KeeperControlledAgent(
        name="character outlook agent",
        sys_prompt="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、动作、神态进行描写。"
                   "注意，你描述的信息应超出被提供的信息的范围，且不允许进行心理描写。"
                   "除非明确要求，否则不允许有褒贬之意。尽量简短、白描。"
                   "以“有一位”开头，开始你的叙述。",
        model_config_name="qwen-max",
        use_memory=True
    )
    character_outlook_agent(npc.get_outlook())

    # scene_memory_agent = KeeperControlledAgent(
    #     name="scene memory agent",
    #     sys_prompt="你是一个场景历史助手。你将得到在该场景的事件的描述，在这些事件会对场景产生持久的影响的前提下，以一句话概括这些事件。"
    #                "概括事件时，只涉及到事物，不涉及到人物。"
    #                "如果事件不会产生持久的影响，返回NULL。",
    #     model_config_name="qwen-max",
    #     use_memory=True
    # )
    # scene_memory_agent(f"场景:{s.get_panorama_prompt()} \n 事件：阿特拉斯不小心打翻了水杯，地面上到处都是水")
    #
    # check_agent = KeeperControlledAgent(
    #     name="check agent",
    #     sys_prompt="你是一个COC检定助手。你将得到某一行动的描述，你需要判断为完成这一行动，是否需要进行“检定”。"
    #                "“检定”（Check或Roll）是指玩家为了确定其角色是否成功完成某个行动、克服特定难度或获取信息而进行的一种游戏机制。"
    #                "具体操作时，玩家需要依据角色的对应技能数值和游戏规则投掷骰子，通过比较投掷结果与目标难度值来判断行动是否成功。"
    #                "例如："
    #                "当角色尝试撬锁时，可能需要进行“撬锁”技能检定。"
    #                "当角色试图察觉环境中的微妙线索时，可能需要进行“侦查”或“灵感”检定。"
    #                "当角色直面恐怖的事物，可能会触发“理智”（Sanity）检定，以决定角色的精神状态是否保持稳定。"
    #                "从以下属性或技能中选择需要进行检定的技能：聆听，侦查，图书馆使用，斗殴，说服，恐吓，魅惑，理智，话术，体操，闪避，医术，急救。"
    #                "根据接下来的描述，判断是否需要进行检定，并决定其困难级别（一般、困难、极难、不可能）。"
    #                "例如，在受一般程度噪音干扰的情况尝试进行偷听，需要进行聆听检定，其困难级别将为困难，如下回答即可："
    #                "聆听（困难）",
    #     model_config_name="qwen-max",
    #     use_memory=True
    # )
    # check_agent(f"KP：由于遭到动乱，图书馆的这片书架全部倒塌，书乱作一团。\n阿特拉斯：我要尝试从中找到我要的书。")
    #
    # check_agent = KeeperControlledAgent(
    #     name="check agent",
    #     sys_prompt="你是一个COC检定助手。你将得到某一行动的描述，你需要判断为完成这一行动，是否需要进行“检定”。"
    #                "“检定”（Check或Roll）是指玩家为了确定其角色是否成功完成某个行动、克服特定难度或获取信息而进行的一种游戏机制。"
    #                "具体操作时，玩家需要依据角色的对应技能数值和游戏规则投掷骰子，通过比较投掷结果与目标难度值来判断行动是否成功。"
    #                "例如："
    #                "当角色尝试撬锁时，可能需要进行“撬锁”技能检定。"
    #                "当角色试图察觉环境中的微妙线索时，可能需要进行“侦查”或“灵感”检定。"
    #                "当角色直面恐怖的事物，可能会触发“理智”（Sanity）检定，以决定角色的精神状态是否保持稳定。"
    #                "从以下属性或技能中选择需要进行检定的技能：聆听，侦查，图书馆使用，斗殴，说服，恐吓，魅惑，理智，话术，体操，闪避，医术，急救。"
    #                "根据接下来的描述，判断是否需要进行检定，并决定其困难级别（一般、困难、极难、不可能）。"
    #                "例如，在受一般程度噪音干扰的情况尝试进行偷听，需要进行聆听检定，其困难级别将为困难，如下回答即可："
    #                "聆听（困难）",
    #     model_config_name="qwen-max",
    #     use_memory=True
    # )
    # check_agent(f"KP：就在这时，从你视觉的死角处，一个黑影猛然窜出，当你意识到时，什么东西已经袭向了你。\n阿特拉斯：闪开！")
    #
    # check_agent = KeeperControlledAgent(
    #     name="check agent",
    #     sys_prompt="你是一个COC检定助手。你将得到某一行动的描述，你需要判断为完成这一行动，是否需要进行“检定”。"
    #                "“检定”（Check或Roll）是指玩家为了确定其角色是否成功完成某个行动、克服特定难度或获取信息而进行的一种游戏机制。"
    #                "具体操作时，玩家需要依据角色的对应技能数值和游戏规则投掷骰子，通过比较投掷结果与目标难度值来判断行动是否成功。"
    #                "例如："
    #                "当角色尝试撬锁时，可能需要进行“撬锁”技能检定。"
    #                "当角色试图察觉环境中的微妙线索时，可能需要进行“侦查”或“灵感”检定。"
    #                "当角色直面恐怖的事物，可能会触发“理智”（Sanity）检定，以决定角色的精神状态是否保持稳定。"
    #                "从以下属性或技能中选择需要进行检定的技能：聆听，侦查，图书馆使用，斗殴，说服，恐吓，魅惑，理智，话术，体操，闪避，医术，急救。"
    #                "根据接下来的描述，判断是否需要进行检定，并决定其困难级别（一般、困难、极难、不可能）。"
    #                "例如，在受一般程度噪音干扰的情况尝试进行偷听，需要进行聆听检定，其困难级别将为困难，如下回答即可："
    #                "聆听（困难）"
    #                "此外，理智检定只有一般难度。",
    #     model_config_name="qwen-max",
    #     use_memory=True
    # )
    # check_agent(f"KP：你低下头，脚下一片血红。在那血红延伸开去的方向，堆积着大量的——尸体。")

    command_router_agent = KeeperControlledAgent(
        name="command router agent",
        sys_prompt="你是指令的传达者。根据给出的指令，判断指令需要传达给以下哪些对象。"
                   "注意：指令可能影响多个对象。"
                   "以下是可能成为指令目标的对象："
                   "场景管理器：只接受某些会对环境造成持久影响的指令。"
                   "人物管理器：只接受与登场人物有关的指令。"
                   "战斗管理器：只接受战斗轮开始的指令。"
                   "追逐管理器：只接受追逐轮开始的指令。"
                   "以、为间隔，回答所有接受指令的对象。",
        model_config_name="qwen-max",
        use_memory=True
    )

    npc_manager_agent = KeeperControlledAgent(
        name="npc manager agent",
        sys_prompt="你是人物管理器。根据给出的指令，判断指令需要传达给以下哪些人物。"
                   "指令可能不会直接指名道姓，需要从对象的特征判断是否成为指令的目标。"
                   "注意：指令可能以多个对象为目标。"
                   "以下是可能成为指令目标的对象："
                   "安理：图书管理员，少女\n"
                   "安阳：一位高大的男性\n"
                   "刘毅：馆长\n"
                   "以换行符为间隔，回答所有接受指令的对象的名字。回答的对象必须从上述对象中选出，或者是“无”。",
        model_config_name="qwen-max",
        use_memory=True
    )

    router_result = command_router_agent("阿特拉斯向少女走去。")["content"]
    if "人物管理器" in router_result:
        npc_manager_agent("阿特拉斯向少女走去。")

