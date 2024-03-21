import os
from typing import Union
from loguru import logger

from agents.KeeperControlledAgent import KeeperControlledAgent
from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from scene.Scene import Scene


class SceneManager:
    _config_root_path: str
    _current_scene: Union[Scene, None]
    _panorama_agent: KeeperControlledAgent
    _character_outlook_manager: KeeperControlledAgent

    def __init__(self, config_root_path):
        self._config_root_path = config_root_path

        self._panorama_agent = KeeperControlledAgent(
            name="scene agent",
            sys_prompt="你是一个画面描述助手。根据提供的场景信息和额外提示词，你需要为其生成洛夫·克拉夫特风格的"
                       "画面描述。但是，别提到洛夫·克拉夫特。"
                       "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                       "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                       "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。",
            model_config_name="qwen-max",
            use_memory=True
        )

        self._character_outlook_manager = KeeperControlledAgent(
            name="character outlook agent",
            sys_prompt="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、神态进行描写。"
                       "注意，你描述的信息不应超出被提供的信息的范围，且不允许进行心理描写。"
                       "除非明确要求，否则不允许有褒贬之意。尽量简短、白描。"
                       "以“有一位”开头，开始你的叙述。",
            model_config_name="qwen-max",
            use_memory=True
        )

    def enter_scene(self, scene_name):
        scene_config_path = self._config_root_path + f"/scenes/{scene_name}.yaml"
        self._current_scene = Scene(config_path=scene_config_path)
        logger.info(f"切换为场景：{scene_name}")

    def add_player(self, player_name):
        player_path = self._config_root_path + f"/characters/player_character/{player_name}.yaml"
        player = PlayerCharacter(config_path=player_path)
        self._current_scene.add_player(player)
        logger.info(f"已加载玩家角色：{player_name}")

    def add_npc(self, npc_name):
        npc_path = self._config_root_path + f"/characters/non_player_character/{npc_name}.yaml"
        npc = PlayerCharacter(config_path=npc_path)
        self._current_scene.add_non_player_character(npc)
        logger.info(f"已加载npc：{npc_name}")

    def draw_a_panorama(self):
        self._panorama_agent(self._current_scene.get_panorama_prompt())

    def generate_scene_memory(self, memory):
        self._current_scene.add_memory(memory)

    def save(self):
        self._current_scene.save()

    def character_enter(self, character_name):
        player_path = self._config_root_path + f"/characters/player_characters/{character_name}.yaml"
        npc_path = self._config_root_path + f"/characters/non_player_characters/{character_name}.yaml"
        if os.path.exists(player_path):
            character = PlayerCharacter(config_path=player_path)
            self._current_scene.add_player(character)
            logger.info(f"已加载玩家角色：{character_name}")
        else:
            character = NonPlayerCharacter(config_path=npc_path)
            self._current_scene.add_non_player_character(character)
            logger.info(f"已加载非玩家角色：{character_name}")

    def character_outlook(self, character_name: str):
        self._character_outlook_manager(self._current_scene.get_character(character_name).get_look_prompt())

    # def character_say(self, character_name:str, content: str, expression: str):
    #     self._current_scene.get_character(character_name)(f"进行以角色扮演：\n神态、动作：{expression}，\n说话内容：{content}")

    def character_act(self, character_name:str, act: str):
        self._current_scene.get_character(character_name)(f"进行以下动作的角色扮演：{act}")

    def player_agent(self, player_name):
        return self._current_scene.get_character(player_name)()

