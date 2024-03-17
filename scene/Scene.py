from typing import Dict, List


from character.NonPlayerCharacter import NonPlayerCharacter
from character.PlayerCharacter import PlayerCharacter
from items.BaseItem import BaseItem


class Scene:
    _era: str
    _position: str
    _description: str
    _players: Dict[str, PlayerCharacter]
    _non_player_characters: Dict[str, NonPlayerCharacter]
    _interactive_items: List[BaseItem]
    _runtime_stack: List[str]
    _keeper_commands: List[str]

    def __init__(self,
                 era: str, position: str,
                 description: str,
                 **kwargs):
        self._era = era
        self._position = position
        self._description = description
        self._players = {}
        self._non_player_characters = {}
        self._interactive_items = []
        self._runtime_stack = kwargs.get("runtime_stack", [])
        self._keeper_commands = kwargs.get("keeper_commands", [])

    def add_player(self, character: PlayerCharacter):
        self._players[character.get_name()] = character

    def remove_player(self, name):
        del self._players[name]

    def add_non_player_character(self, character):
        self._non_player_characters[character.get_name()] = character

    def remove_non_player_character(self, name):
        del self._non_player_characters[name]

    def add_interactive_object(self, obj):
        self._interactive_items.append(obj)

    def get_panorama_prompt(self, extra_prompt=""):
        prompt = f"""
         年代：{self._era}，
         地点：{self._position}，

         {self._description}
        """
        if len(self._runtime_stack) > 0:
            runtime_description = "\n".join(self._runtime_stack)
            prompt += f"""
            到目前为止，此处发生了以下事件：
            {runtime_description}
            """
        if len(self._keeper_commands) > 0:
            keeper_commands = "\n".join(self._keeper_commands)
            prompt += f"""
                        进行描述时，还需按照以下要求：
                        {keeper_commands}
                        {extra_prompt}
                        """
        else:
            if len(extra_prompt) > 0:
                prompt += f"""进行描述时，还需按照以下要求：{extra_prompt}"""
        return prompt





if __name__ == '__main__':
    s = Scene("二十一世纪初", "上海市立图书馆",
              "中央有天井，由于是周末，人不多")
    print(s.get_panorama_prompt())
