from abc import abstractmethod
from typing import List, Union, Dict

import yaml

from agents.KeeperControlledAgent import KeeperControlledAgent
from items.BaseItem import BaseItem


class BaseCharacter:
    _name: str
    _outlook: str
    _age: str
    _tone: str
    _description: str
    _visible_in_scene: bool

    _items: List[BaseItem]

    _ability: Dict[str, int]

    def __init__(self, **kwargs):
        config = kwargs
        config_path = kwargs.get("config_path", None)
        if config_path:
            with open(config_path, 'r', encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)

        self._name = config.get("name")
        self._outlook = config.get("outlook")
        self._age = config.get("age", "")
        self._tone = config.get("tone", "")
        self._personality = config.get("personality", "")
        self._description = config.get("description", "")
        self._visible_in_scene = config.get("visible", True)
        self._items = config.get("items", [])

        self._ability = config.get("ability")
        self._skill = config.get("skill")

    def get_name(self):
        return self._name

    def get_look_prompt(self):
        if self._visible_in_scene:
            return self._outlook
        return ""

    @abstractmethod
    def get_agent(self):
        pass

    def get_skill_value(self, skill_name):
        return self._skill[skill_name]