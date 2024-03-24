from abc import abstractmethod
from typing import List, Union, Dict

import yaml

from agents.KeeperControlledAgent import KeeperControlledAgent
from items.BaseItem import BaseItem


class BaseCharacter:
    _config_path: str
    _memory: List[str]
    _name: str
    _outlook: str
    _age: str
    _tone: str
    _description: str

    _ability: Dict[str, int]
    _stable_diffusion_tags: List[str]

    def __init__(self, **kwargs):
        config = kwargs
        self._config_path = kwargs.get("config_path", None)
        if self._config_path:
            with open(self._config_path, 'r', encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)

        self._name = config.get("name")
        self._outlook = config.get("outlook")
        self._age = config.get("age", "")
        self._tone = config.get("tone", "")
        self._personality = config.get("personality", "")
        self._description = config.get("description", "")
        self._stable_diffusion_tags = config.get("stable_diffusion_tags", [])

        self._ability = config.get("ability")
        self._skill = config.get("skill")

        self._memory = config.get("memory", [])

    def get_name(self):
        return self._name

    def get_outlook(self):
        return self._outlook

    @abstractmethod
    def get_agent(self):
        pass

    def get_ability_or_skill_value(self, skill_or_ability_name):
        if skill_or_ability_name in self._skill:
            return self._skill[skill_or_ability_name]
        elif skill_or_ability_name in self._ability:
            return self._ability[skill_or_ability_name]
        return self._skill[skill_or_ability_name] if skill_or_ability_name in self._skill else None

    def get_stable_diffusion_tags(self):
        return self._stable_diffusion_tags

    @abstractmethod
    def serialize(self):
        pass

    @abstractmethod
    def save(self, config_root_path):
        pass

    def add_memory(self, memory):
        self._memory.append(memory)

    def get_ability_and_skill(self):
        ability_and_skill_dict = {}
        for name in self._ability:
            ability_and_skill_dict[name] = self._ability[name]
        for name in self._skill:
            ability_and_skill_dict[name] = self._skill[name]
        return ability_and_skill_dict