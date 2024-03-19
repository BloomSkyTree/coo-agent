from typing import List

from agentscope.message import Msg

from agents.KeeperControlledAgent import KeeperControlledAgent
from character.BaseCharacter import BaseCharacter


class NonPlayerCharacter(BaseCharacter):
    _short_term_memory: List[str]
    _long_term_memory: List[str]

    _agent: KeeperControlledAgent

    def __init__(self,
                 name: str,
                 outlook: str,
                 **kwargs):
        super().__init__(name, outlook, **kwargs)

        self._short_term_memory = []
        self._long_term_memory = []

        character_prompt = f"""
                    扮演以下角色：
                    名字：{self._name}
                    外貌: {self._outlook}

                    {self._description}
                """
        if self._age:
            character_prompt += f"\n年龄：{self._age}"
        if self._tone:
            character_prompt += f"\n年龄：{self._age}"
        if self._personality:
            character_prompt += f"\n性格：{self._personality}"
        if self._description:
            character_prompt += f"\n描述：{self._description}"

        character_prompt += f"\n在扮演时，你只作为{self.get_name()}进行扮演。不允许扮演其他角色。" \
                            f"对于没有在上文中出现名字，且逻辑上与自己无关的人，都将其作为陌生人看待。"

        self._agent = KeeperControlledAgent(
            name=self._name,
            sys_prompt=character_prompt,
            model_config_name=kwargs.get("model_config_name"),
            use_memory=True
        )

    def __call__(self, *args, **kwargs):
        return self._agent(*args, **kwargs)

    def generate_long_term_memory(self):
        return self._agent("根据到目前为止的交互，概括你关心的内容，简要说明你的看法、态度。"
                           "以回忆过去的口吻，说明当时的场景，叙述自己的印象。"
                           "如果没有你特别关心、觉得应该记住的事，如下回答："
                           "无大事发生。")
