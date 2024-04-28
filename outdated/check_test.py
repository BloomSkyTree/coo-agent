from agentscope.message import Msg

from agents.KeeperControlledAgent import KeeperControlledAgent

if_check_agent = KeeperControlledAgent(
    name="检定判断器",
    sys_prompt="你是一个检定判断器。根据剧本内容，你需要判断某一角色当前的行为是否需要进行检定，并以JSON格式回答。\n"
               "如果该角色没有进行什么特别的行动，或其目标从常理来说即使不依赖特定技能也能达成，则不需要检定，返回：{\"need_check\": false, \"possible\":true}\n"
               "如果该角色的目标从常理来无论如何都不可能达成，则不需要检定，回答：返回：{\"need_check\": false, \"possible\":false}\n"
               "如果该角色的目标视其自身能力或技能而言可能成功也可能失败，则回答：返回：{\"need_check\": true, \"possible\":true}。",
    model_config_name="qwen-local",
    use_memory=False
)

check_difficulty_agent = KeeperControlledAgent(
    name="检定级别判断器",
    sys_prompt="你是一个检定判断器。根据剧本内容，你需要判断某一角色当前的行为需要进行何种检定，并以JSON格式回答。\n"
               "你的回答必须包含以下两个字段：\n"
               "skill_or_ability_name：需要进行检定的技能或能力的名称，类型为字符串，可选值包括：侦查、图书馆使用、聆听、闪避、斗殴、潜行、说服、话术、魅惑、恐吓、偷窃、神秘学、克苏鲁神话。\n"
               "difficulty：角色行为成功难易度，类型为字符串，可选值包括：普通、困难、极难。\n"
               "为了防止误解，以下是一些有歧义的技能的定义：\n"
               "侦查：这项技能允许使用者发现被隐藏起来的东西或线索，觉察常人难以意识到的异象。\n"
               "潜行：这项技能在使用者尝试主动地隐蔽自己的行迹、动静时适用。\n"
               "聆听：这项技能在使用者尝试通过听力等非视觉感官获取情报时适用。\n"
               "话术：话术特别限定于言语上的哄骗，欺骗以及误导。\n"
               "魅惑：魅惑允许通过许多形式来使用，包括肉体魅力、诱惑、奉承或是单纯令人感到温暖的人格魅力。魅惑可能可以被用于迫使某人进行特定的行动，但是不会是与个人日常举止完全相反的行为。\n"
               "神秘学：这项技能反应了对神秘学知识的了解。\n"
               "克苏鲁神话：这项技能反应了对非人类（洛夫克拉夫特的）克苏鲁神话的了解。\n"
               "以下是困难级别相关的说明：\n"
               "普通：具有对应的技能或能力，在正常发挥的情况下能办到。\n"
               "困难：即使具有对应的技能或能力，也因为自身状态或环境的恶劣，使得达成的难度更上一层楼。\n"
               "极难：对于常人来说，依赖本身技能或能力很难办到，需要超常发挥且运气极佳才能达成；又或者自身状态或环境极端恶劣，使得正常发挥几乎不可能。\n"
               "例如，一个人在尝试讨好另一个人，取得另一个人的好印象，需要进行普通级别的魅惑检定，你应返回：{\"skill_or_ability_name\":\"魅惑\", \"difficulty\":\"普通\"}",
    model_config_name="qwen-local",
    use_memory=False
)

if_check_agent(Msg(name="if check agent", content="待判断行动：爱丽丝侧耳倾听，希望能听到什么蛛丝马迹的声音。\n"
                                                  "以JSON格式给出回答。"))

check_difficulty_agent(Msg(name="if check agent", content="待判断行动：爱丽丝侧耳倾听，希望能听到什么蛛丝马迹的声音。\n"
                                                          "以JSON格式给出回答。"))
