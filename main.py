import agentscope

from agents.KeeperControlledAgent import KeeperControlledAgent
from character.NonPlayerCharacter import NonPlayerCharacter
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
        outlook="少女，十七八岁，黑长直，样貌一般，戴眼镜",
        description="氛围阴郁，似乎很忙，处于不是很有耐心的状态。其性格比较沉闷，言语简短，不苟言笑。兼职。"
    )
    s.add_non_player_character(npc)

    panorama_agent = KeeperControlledAgent(
        name="scene agent",
        sys_prompt="你是一个画面描述助手。根据提供的场景信息和额外提示词，你需要为其生成洛夫·克拉夫特风格的"
                   "画面描述。但是，别提到洛夫·克拉夫特。"
                   "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                   "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                   "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。",
        model_config_name="qwen-max",
        use_memory=True
    )
    panorama_agent(s.get_panorama_prompt())

    character_outlook_agent = KeeperControlledAgent(
        name="character outlook agent",
        sys_prompt="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、动作、神态进行描写。"
                   "注意，你描述的信息应超出被提供的信息的范围，且不允许进行心理描写。"
                   "以“有一位”开头，开始你的叙述。",
        model_config_name="qwen-max",
        use_memory=True
    )
    character_outlook_agent(npc.get_look_prompt())
