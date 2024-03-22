import os
import random
from typing import Union

from agentscope import msghub
from agentscope.memory import TemporaryMemory
from agentscope.msghub import MsgHubManager
from loguru import logger

from agents.KeeperControlledAgent import KeeperControlledAgent
from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from scene.Scene import Scene


class SceneManager:
    _config_root_path: str
    _current_scene: Union[Scene, None]
    _panorama_agent: KeeperControlledAgent
    _character_outlook_agent: KeeperControlledAgent
    _script_listener_agent: KeeperControlledAgent

    def __init__(self, config_root_path):
        self._config_root_path = config_root_path

        self._panorama_agent = KeeperControlledAgent(
            name="场景描述",
            sys_prompt="你是一个画面描述助手。根据提供的场景信息和额外提示词，你需要为其生成洛夫·克拉夫特风格的"
                       "画面描述。但是，别提到洛夫·克拉夫特。"
                       "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                       "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                       "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。",
            model_config_name="qwen-max",
            use_memory=True
        )

        self._character_outlook_agent = KeeperControlledAgent(
            name="人物形象描述",
            sys_prompt="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、神态进行描写。"
                       "注意，你描述的信息不应超出被提供的信息的范围，且不允许进行心理描写。"
                       "除非明确要求，否则不允许有褒贬之意。尽量简短、白描。"
                       "以“有一位”开头，开始你的叙述。",
            model_config_name="qwen-max",
            use_memory=True
        )

        self._script_listener_agent = KeeperControlledAgent(
            name="script listener agent",
            sys_prompt="",
            model_config_name="qwen-max",
            use_memory=True
        )

        self._check_agent = KeeperControlledAgent(
            name="检定管理器",
            sys_prompt="你是一个COC智能检定管理器。根据剧本内容，你需要判断某一角色是否需要进行检定，并进行不同的python代码执行。"
                       "如果该角色没有进行什么特别的行动，或其目标从常理来说即使不依赖特定技能也能达成，则不需要检定，self.do_not_need_check(character_name: str)方法。\n"
                       "如果该角色的目标从常理来无论如何都不可能达成，则不需要检定，self.impossible_check(character_name: str)方法。\n"
                       "如果需要进行检定，则需要判断检定的困难级别（普通，困难，极难）。\n"
                       "以下是困难级别相关的说明：\n"
                       "普通：具有对应的技能，在正常发挥的情况下能办到。\n"
                       "困难：即使具有对应的技能，也因为自身状态或环境的恶劣，使得达成的难度更上一层楼。\n"
                       "极难：对于常人来说，依赖本身技能很难办到，需要超常发挥且运气极佳才能达成；又或者自身状态或环境极端恶劣，使得正常发挥几乎不可能。\n"
                       "如果该角色需要检定，self.do_check(character_name: str, skill:str, difficulty: str)方法。\n"
                       "其中，skill为需要进行检定的技能名称，可选值包括：侦查、图书馆使用、聆听、闪避、斗殴、潜行、说服、话术、魅惑、恐吓、偷窃、神秘学、克苏鲁神话。\n"
                       "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
                       "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
            model_config_name="qwen-max",
            use_memory=True
        )

    def enter_scene(self, scene_name):
        scene_config_path = self._config_root_path + f"/scenes/{scene_name}.yaml"
        self._current_scene = Scene(config_path=scene_config_path)
        self._current_scene.add_listener(self._script_listener_agent)
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
        message = self._panorama_agent(self._current_scene.get_panorama_prompt())
        self._script_listener_agent.observe(message)

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
        outlook_message = self._character_outlook_agent(
            self._current_scene.get_character(character_name).get_look_prompt()
        )
        self._script_listener_agent.observe(outlook_message)

    def character_act(self, character_name: str, act: str):
        check_result = self.judge_check(character_name, act)
        if check_result is None:
            rp_message = self._current_scene.get_character(character_name)(f"进行以下动作的角色扮演：{act}")
        else:
            rp_message = self._current_scene.get_character(character_name)(f"进行以下动作的角色扮演：{act}，且该动作的结果为：{check_result}\n注意，在扮演和描述时，不能直接说出成功与否。")
        if rp_message is not None:
            self._script_listener_agent.observe(rp_message)


    def player_role_play(self, player_name, role_play):
        rp_message = self._current_scene.player_role_play(player_name, role_play)
        if rp_message is not None:
            self._script_listener_agent.observe(rp_message)
            self.judge_check(player_name, role_play)

    def get_script(self):
        memory = self._script_listener_agent.memory
        return memory.get_memory(memory.size())

    def do_check(self, character_name: str, skill: str, difficulty: str):
        level_mapping = {
            "大成功": 4,
            "极难": 3,
            "困难": 2,
            "普通": 1,
            "失败": 0,
            "大失败": -1
        }
        character = self._current_scene.get_character(character_name)
        skill_value = character.get_skill_value(skill)
        check = random.randint(1, 100)
        percent = float(check) / float(skill_value)
        check_info = f"{character_name}进行了{skill}检定，{check}/{skill_value}，"
        if check > 95:
            check_info += "大失败！"
        elif check <= 5:
            check_info += "大成功！"
        elif percent > 1:
            check_info += "失败了。"
        elif percent >= 1 / 2:
            if level_mapping[difficulty] > 1:
                check_info += "未达到所需级别，失败了。"
            else:
                check_info += "普通成功，完成了目标。"
        elif percent >= 1 / 4:
            if level_mapping[difficulty] > 2:
                check_info += "未达到所需级别，失败了。"
            else:
                check_info += "困难成功，完成了目标。"
        else:
            check_info += "极难成功，完成了目标。"

        logger.info(check_info)
        return check_info


    def judge_check(self, character, act):
        scene_description = self._current_scene.get_panorama_prompt()
        script = "\n".join([f"{m['name']}：{m['content']}" for m in self.get_script()])
        prompt = f"场景如下：\n{scene_description}\n剧本如下：\n{script}\n\n判断以下内容是否需要检定，并进行对应的函数调用：\n" \
                 f"{character} 尝试进行以下言行：{act}"
        check = self._check_agent(prompt)["content"]
        check_result = eval(check)
        self._check_agent.memory.clear()
        return check_result

    def do_not_need_check(self, character_name: str):
        logger.info(f"{character_name}的行动不需要进行检定。")

    def impossible_check(self, character_name: str):
        logger.info(f"{character_name}的行动不可能达成，无需进行检定。")
