from typing import List, Sequence, Union

import yaml
from typing import Type
from characters.BaseCharacter import BaseCharacter
from utils.llm.BaseLlm import BaseLlm
from utils.llm.LlmFactory import LlmFactory
from utils.llm.LlmMessage import LlmMessage


class NonPlayerCharacter(BaseCharacter):
    _belong_to_scene: Type["Scene"]

    _agent: BaseLlm
    _llm_model_name: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self._config_path:
            with open(self._config_path, 'r', encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        self._llm_model_name = config.get("llm_model_name", "llama")

        self._agent = LlmFactory.get_llm_by_model_name(self._llm_model_name, self.generate_system_prompt())

    def __call__(self, message: Union[str, LlmMessage]):
        if isinstance(message, LlmMessage):
            return self._agent.chat(query=message, max_new_tokens=512)
        elif isinstance(message, str):
            message_msg = LlmMessage(role="npc role play agent", content=message)
            return self._agent.chat(query=message_msg, max_new_tokens=512)
        raise ValueError(f"未支持的消息类型：{type(message)}")

    def generate_system_prompt(self):
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

        if self._memory:
            character_prompt += "你的记忆：\n"
        for memory in self._memory:
            character_prompt += f"{memory}\n"

        character_prompt += f"\n在扮演时，你只作为{self.get_name()}进行扮演。不允许扮演其他角色。" \
                            f"如果有关于自己记忆的描述，则需要根据记忆进行扮演。" \
                            f"对于没有在上文中出现名字，且逻辑上与自己无关的人，都将其作为陌生人看待。" \
                            f"如果陌生人没有自我介绍，则你不应当知道其名字。\n" \
                            f"扮演时，不一定要说话，也可以只做动作或表情。\n" \
                            f"扮演时的格式如下：\n" \
                            f"自己的名字：（表情，神态，动作，描写）“说话的内容（如果不说话，则不需要此部分）”\n" \
                            f"例如：\n" \
                            f"{self.get_name()}：（伸出手，仿佛在抚摸空气中看不见的什么东西）“这样……就可以了。”"

        return [LlmMessage(role="system", content=character_prompt)]

    def generate_long_term_memory(self):
        self._agent.sys_prompt = self.generate_system_prompt()
        message = LlmMessage(content="根据到目前为止的交互，概括你关心的内容，简要说明你的看法、态度。"
                                     "以回忆过去的口吻，说明当时的场景，叙述自己的印象。"
                                     "如果没有你特别关心、觉得应该记住的事，如下回答："
                                     "无大事发生。")
        return self._agent.chat(query=message, max_new_tokens=1024)

    def set_scene(self, scene):
        self._belong_to_scene = scene

    def get_agent(self):
        return self._agent

    def serialize(self):
        return {
            "name": self._name,
            "outlook": self._outlook,
            "age": self._age,
            "tone": self._tone,
            "description": self._description,
            "personality": self._personality,
            "ability": self._ability,
            "skill": self._skill,
            "stable_diffusion_tags": self._stable_diffusion_tags,
            "memory": self._memory
        }

    def save(self, config_root_path):
        if self._config_path is None:
            self._config_path = config_root_path + f"/characters/non_player_characters/{self._name}.yaml"
        content = self.serialize()
        with open(self._config_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(content, yaml_file, allow_unicode=True, sort_keys=False)
