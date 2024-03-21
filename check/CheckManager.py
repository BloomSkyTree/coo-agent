from agents.KeeperControlledAgent import KeeperControlledAgent


class CheckManager:

    def __init__(self):
        self._agent = KeeperControlledAgent(
            name="检定管理器",
            sys_prompt="你是一个COC智能检定管理器。根据最后接受到的指令类型不同，你需要进行不同的python代码执行。\n"
                       "当指令是判断检定需求时，调用check_manager.determine_check()方法。\n"
                       "当输入是要求某一人物进行检定（有时会被表述为“过一个……”）时，调用do_check(character_name:str, check: str, check_difficulty:str)方法。\n"
                       "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
                       "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
            model_config_name="qwen-max",
            use_memory=True
        )

    def determine_check(self):
        self._agent("")
