

import yaml

from characters.BaseCharacter import BaseCharacter
from utils.llm.BaseLlm import BaseLlm


class PlayerCharacter(BaseCharacter):
    _agent: BaseLlm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __call__(self, *args, **kwargs):
        raise Exception("不能对PlayerCharacter进行调用。")

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
            self._config_path = config_root_path + f"/characters/player_characters/{self._name}.yaml"
        content = self.serialize()
        with open(self._config_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(content, yaml_file, allow_unicode=True, sort_keys=False)
