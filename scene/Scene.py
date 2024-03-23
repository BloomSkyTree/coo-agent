import os
from collections import OrderedDict
from typing import Dict, List

import yaml
from agentscope.message import Msg
from agentscope.msghub import MsgHubManager, msghub
from loguru import logger

from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from items.BaseItem import BaseItem


class Scene:
    _era: str
    _position: str
    _description: str
    _players: Dict[str, PlayerCharacter]
    _non_player_characters: Dict[str, NonPlayerCharacter]
    _interactive_items: List[BaseItem]
    _memory: List[str]
    _keeper_commands: List[str]

    _config_path: str
    _message_hub: MsgHubManager

    def __init__(self, **kwargs):
        config = kwargs
        self._config_path = kwargs.get("config_path", None)
        if self._config_path:
            with open(self._config_path, 'r', encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        self._era = config.get("era")
        self._position = config.get("position")
        self._description = config.get("description")
        self._players = {}
        self._non_player_characters = {}
        self._interactive_items = []
        self._memory = config.get("memory", [])
        self._keeper_commands = config.get("keeper_commands", [])

        self._message_hub = msghub(participants=[])

    def add_player(self, character: PlayerCharacter):
        self._players[character.get_name()] = character

    def remove_player(self, name):
        del self._players[name]

    def add_non_player_character(self, character):
        self._non_player_characters[character.get_name()] = character
        self._message_hub.add(character.get_agent())

    def remove_non_player_character(self, name):
        character = self._non_player_characters[name]
        self._message_hub.delete(character.get_agent())
        del self._non_player_characters[name]

    def add_interactive_object(self, obj):
        self._interactive_items.append(obj)

    def get_panorama_prompt(self, extra_prompt=""):
        prompt = f"""
         年代：{self._era}，
         地点：{self._position}，

         {self._description}
        """
        if len(self._memory) > 0:
            memory_description = "\n".join(self._memory)
            prompt += f"""
            到目前为止，此处发生了以下事件：
            {memory_description}
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

    def add_memory(self, memory):
        self._memory.append(memory)

    def serialize(self):
        return {
            "era": self._era,
            "position": self._position,
            "description": self._description,
            "interactive_items": self._interactive_items,
            "memory": self._memory,
            "keeper_commands": self._keeper_commands
        }

    def save(self):
        content = self.serialize()
        with open(self._config_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(content, yaml_file, allow_unicode=True, sort_keys=False)

    def get_character(self, character_name):
        if character_name in self._non_player_characters:
            return self._non_player_characters[character_name]
        elif character_name in self._players:
            return self._players[character_name]
        else:
            return None

    def get_character_list(self):
        return list(self._non_player_characters.values()) + list(self._players.values())

    def player_role_play(self, player_name: str, role_play: str):
        if player_name in self._players:
            message = Msg(
                name=player_name,
                content=f"{player_name}：{role_play}"
            )
            self._message_hub.broadcast(message)
            return message
        else:
            logger.warning(f"未找到对应玩家：{player_name}，忽略此次消息。")
            return None

    def add_listener(self, agent):
        self._message_hub.add(agent)
