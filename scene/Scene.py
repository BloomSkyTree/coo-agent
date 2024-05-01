
from typing import Dict, List

import yaml
from loguru import logger

from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from outdated.items.BaseItem import BaseItem
from utils.llm.BaseLlm import BaseLlm
from utils.llm.LlmMessage import LlmMessage


class Scene:
    _name: str
    _era: str
    _position: str
    _description: str
    _players: Dict[str, PlayerCharacter]
    _non_player_characters: Dict[str, NonPlayerCharacter]
    _interactive_items: List[BaseItem]
    _memory: List[str]
    _keeper_commands: List[str]

    _stable_diffusion_tags: List[str]

    _config_path: str
    _existed_agent_name: List[str]
    _message_hub: Dict[str, BaseLlm]

    def __init__(self, **kwargs):
        config = kwargs
        self._config_path = kwargs.get("config_path", None)
        if self._config_path:
            with open(self._config_path, 'r', encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.FullLoader)
        self._name = config.get("name")
        self._era = config.get("era")
        self._position = config.get("position")
        self._description = config.get("description")
        self._players = {}
        self._non_player_characters = {}
        self._interactive_items = []
        self._memory = config.get("memory", [])
        self._keeper_commands = config.get("keeper_commands", [])
        self._stable_diffusion_tags = config.get("stable_diffusion_tags", [])

        self._message_hub = {}

    def get_name(self):
        return self._name

    def add_player(self, character: PlayerCharacter):
        self._players[character.get_name()] = character

    def remove_player(self, name):
        del self._players[name]

    def add_non_player_character(self, character):
        self._non_player_characters[character.get_name()] = character
        self._message_hub[character.get_name()] = (character.get_agent())

    def remove_non_player_character(self, name):
        # character = self._non_player_characters[name]
        del self._message_hub[name]
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
            "name": self._name,
            "era": self._era,
            "position": self._position,
            "description": self._description,
            "interactive_items": self._interactive_items,
            "memory": self._memory,
            "keeper_commands": self._keeper_commands,
            "stable_diffusion_tags": self._stable_diffusion_tags
        }

    def save(self, config_root_path):
        content = self.serialize()
        if not self._config_path:
            self._config_path = config_root_path + f"/scenes/{self._name}.yaml"
        with open(self._config_path, "w", encoding="utf-8") as yaml_file:
            yaml.dump(content, yaml_file, allow_unicode=True, sort_keys=False)
        for character in self.get_character_list():
            character.save(config_root_path)

    def get_character(self, character_name):
        if character_name in self._non_player_characters:
            return self._non_player_characters[character_name]
        elif character_name in self._players:
            return self._players[character_name]
        else:
            return None

    def broadcast(self, message):
        for agent in self._message_hub.values():
            agent.add_memory(message)

    def get_character_list(self):
        return list(self._non_player_characters.values()) + list(self._players.values())

    def player_role_play(self, player_name: str, role_play: str):
        if player_name in self._players:
            message = LlmMessage(
                role=player_name,
                content=f"{player_name}：{role_play}"
            )
            self.broadcast(message)
            return message
        else:
            logger.warning(f"未找到对应玩家：{player_name}，忽略此次消息。")
            return None

    def add_listener(self, name, agent):
        self._message_hub[name] = agent

    def get_stable_diffusion_tags(self):
        return self._stable_diffusion_tags
