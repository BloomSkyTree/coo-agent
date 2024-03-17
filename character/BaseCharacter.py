from typing import List, Union

from items.BaseItem import BaseItem


class BaseCharacter:
    _name: str
    _outlook: str
    _age: Union[str, None]
    _description: str
    _visible_in_scene: bool

    _items: List[BaseItem]

    def __init__(self,
                 name: str,
                 outlook: str,
                 **kwargs):
        self._name = name
        self._outlook = outlook
        self._age = kwargs.get("age", "")
        self._description = kwargs.get("description", "")
        self._visible_in_scene = kwargs.get("visible", True)

    def get_name(self):
        return self._name

    def get_look_prompt(self):
        if self._visible_in_scene:
            return self._outlook + f"({self._description})"
        return ""
