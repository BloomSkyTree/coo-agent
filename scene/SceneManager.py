import os
import random
from http import HTTPStatus
from pathlib import PurePosixPath
from typing import Union
from urllib.parse import unquote, urlparse

import requests
from dashscope import ImageSynthesis

os.environ["DASHSCOPE_API_KEY"] = "sk-d1c122e76c8a4d11b78b3734e48960c6"

from agentscope import msghub
from agentscope.memory import TemporaryMemory
from agentscope.message import Msg
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
    _illustration_agent: KeeperControlledAgent
    _character_outlook_agent: KeeperControlledAgent
    _script_listener_agent: KeeperControlledAgent
    _scene_manager_agent: KeeperControlledAgent
    _stable_diffusion_agent: KeeperControlledAgent

    _current_illustration_path: Union[str, None]

    def __init__(self, config_root_path):
        self._config_root_path = config_root_path

        self._scene_manager_agent = KeeperControlledAgent(
            name="场景管理器",
            sys_prompt="你是一个智能场景管理器。根据接受到的输入类型不同，你需要进行不同的python代码执行。\n"
                       "输入有以下几种类型："
                       "进入、开启、启用场景：调用scene_manager.enter_scene(scene_name: str)方法。"
                       "对场景进行描绘、与周围的景物相关（人物外貌的描述不在此列）时：调用scene_manager.draw_a_panorama()方法。。\n"
                       "对场景本身或场景中的物件造成持久的影响时：调用scene_manager.generate_scene_memory(full_command: str)\n"
                       "对场景进行归档、保存或存档时：调用scene_manager.save()\n"
                       "要求绘制即时插图时：调用scene_manager.illustrate()\n"
                       "对人物外貌进行描述时：调用scene_manager.character_outlook(character_name:str)方法。\n"
                       "描述一个人物在进行某一行动（登场不计入在内）时，调用scene_manager.character_act(character_name:str, act: str)方法，其中act字段应包含原始指令中对动作的详细描述。\n"
                       "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
                       "根据情况不同，若同时满足上述的多种场合，需要进行多个方法调用。调用时，顺序与说明时的顺序一致，由上到下。"
                       "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
            model_config_name="qwen-max",
            use_memory=True
        )

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

        self._illustration_agent = KeeperControlledAgent(
            name="即时描述",
            sys_prompt="你是一个画面描述助手。根据提供的场景信息和剧本信息，你需要为其生成画面背景、人物样貌、衣着等画面描述。"
                       "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                       "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                       "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。"
                       "注意，Keeper相当于旁白，不是登场人物。",
            model_config_name="qwen-max",
            use_memory=True
        )

        self._stable_diffusion_agent = KeeperControlledAgent(
            name="stable diffusion agent",
            sys_prompt="你是一个画面总结助手，根据所提供的画面信息，你需要用英文标签式的形式对画面进行总结概括。"
                       "在总结时，优先列举最重要的画面元素，例如场景的氛围、构图，人物的数量、外表、衣着、动作；尽可能简短，不要超过75个英文单词。"
                       "描述中不许出现人物的名字，优先以1girl和1boy之类的标签指代。\n"
                       "例：一个穿着白色裙子的金发少女站在河边\n"
                       "其结果可以为：1girl, white dress, blonde hair, standing, river\n"
                       "回答时，标签使用英文逗号分隔。",
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
                       "普通：具有对应的技能或能力，在正常发挥的情况下能办到。\n"
                       "困难：即使具有对应的技能或能力，也因为自身状态或环境的恶劣，使得达成的难度更上一层楼。\n"
                       "极难：对于常人来说，依赖本身技能或能力很难办到，需要超常发挥且运气极佳才能达成；又或者自身状态或环境极端恶劣，使得正常发挥几乎不可能。\n"
                       "如果该角色需要检定，self.do_check(character_name: str, skill_or_ability_name:str, difficulty: str)方法。\n"
                       "其中，skill_or_ability_name为需要进行检定的技能名称，可选值包括：侦查、图书馆使用、聆听、闪避、斗殴、潜行、说服、话术、魅惑、恐吓、偷窃、神秘学、克苏鲁神话。\n"
                       "为了防止误解，以下是一些有歧义的技能的定义：\n"
                       "侦查：这项技能允许使用者发现被隐藏起来的东西或线索，觉察常人难以意识到的异象。\n"
                       "潜行：这项技能在使用者尝试主动地隐蔽自己的行迹、动静时适用。\n"
                       "聆听：这项技能在使用者尝试通过听力等非视觉感官获取情报时适用。\n"
                       "话术：话术特别限定于言语上的哄骗，欺骗以及误导。\n"
                       "魅惑：魅惑允许通过许多形式来使用，包括肉体魅力、诱惑、奉承或是单纯令人感到温暖的人格魅力。魅惑可能可以被用于迫使某人进行特定的行动，但是不会是与个人日常举止完全相反的行为。"
                       "神秘学：这项技能反应了对神秘学知识的了解。"
                       "克苏鲁神话：这项技能反应了对非人类（洛夫克拉夫特的）克苏鲁神话的了解。\n"
                       "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
                       "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
            model_config_name="qwen-max",
            use_memory=True
        )

        self._current_illustration_path = None

    def enter_scene(self, scene_name):
        scene_config_path = self._config_root_path + f"/scenes/{scene_name}.yaml"
        self._current_scene = Scene(config_path=scene_config_path)
        self._current_scene.add_listener(self._script_listener_agent)
        logger.info(f"切换为场景：{scene_name}")

    def draw_a_panorama(self):
        message = self._panorama_agent(self._current_scene.get_panorama_prompt())
        self._script_listener_agent.observe(message)

    def generate_scene_memory(self, memory):
        self._current_scene.add_memory(memory)

    def save(self):
        self._current_scene.save()

    def get_character(self, character_name):
        character = self._current_scene.get_character(character_name)
        if character is None:
            character = self.load_character(character_name)
        return character

    def load_character(self, character_name):
        player_path = self._config_root_path + f"/characters/player_characters/{character_name}.yaml"
        npc_path = self._config_root_path + f"/characters/non_player_characters/{character_name}.yaml"
        if os.path.exists(player_path):
            character = PlayerCharacter(config_path=player_path)
            self._current_scene.add_player(character)
            logger.info(f"已加载玩家角色：{character_name}")
            return character
        elif os.path.exists(npc_path):
            character = NonPlayerCharacter(config_path=npc_path)
            self._current_scene.add_non_player_character(character)
            logger.info(f"已加载非玩家角色：{character_name}")
            return character
        else:
            return None

    def character_outlook(self, character_name: str):
        character = self.get_character(character_name)
        if character is None:
            logger.warning(f"无法找到名为{character_name}的玩家或非玩家角色。将不会描述其外貌。")
            return
        outlook_message = self._character_outlook_agent(
            self._current_scene.get_character(character_name).get_look_prompt()
        )
        self._script_listener_agent.observe(outlook_message)

    def character_act(self, character_name: str, act: str):
        character = self.get_character(character_name)
        if character is None:
            logger.warning(f"无法找到名为{character_name}的玩家或非玩家角色。当前行动：{act}将会被忽略。")
            return
        check_result = self.judge_check(character_name, act)
        if isinstance(character, PlayerCharacter):
            # self._script_listener_agent.observe(Msg(name="旁白", content=f"{character_name}尝试进行行动：{act}"))
            logger.info(check_result)
        else:
            if check_result is None:
                rp_message = self._current_scene.get_character(character_name)(f"进行以下动作的角色扮演：{act}")
            else:
                rp_message = self._current_scene.get_character(character_name)(
                    f"进行以下动作的角色扮演：{act}，且该动作的结果为：{check_result}\n注意，在扮演和描述时，不能直接说出成功与否。")
            if rp_message is not None:
                self._script_listener_agent.observe(rp_message)

    def player_role_play(self, player_name, role_play):
        self.get_character(player_name)
        rp_message = self._current_scene.player_role_play(player_name, role_play)
        if rp_message is not None:
            self._script_listener_agent.observe(rp_message)
            self.judge_check(player_name, role_play)

    def get_script(self):
        memory = self._script_listener_agent.memory
        return memory.get_memory(memory.size())

    def do_check(self, character_name: str, skill_or_ability_name: str, difficulty: str):
        level_mapping = {
            "大成功": 4,
            "极难": 3,
            "困难": 2,
            "普通": 1,
            "失败": 0,
            "大失败": -1
        }
        # 能执行到这，必然是存在对应角色的
        character = self.get_character(character_name)
        # 如果给出的困难级别不在预设中，默认转为普通难度
        if difficulty not in level_mapping:
            difficulty = "普通"
        skill_or_ability_value = character.get_ability_or_skill_value(skill_or_ability_name)
        if skill_or_ability_value is None:
            logger.warning(f"技能{skill_or_ability_name}不存在。将转变为幸运检定。")
            return self.do_check(character_name, "幸运", difficulty)
        check = random.randint(1, 100)
        percent = float(check) / float(skill_or_ability_value)
        check_info = f"{character_name}进行了{skill_or_ability_name}检定，{check}/{skill_or_ability_value}，"
        if check > 95:
            check_info += "大失败！不但目标无法成功，还会发生一些糟糕、滑稽的事情。"
        elif check <= 5:
            check_info += "大成功！不仅目标完美达成，而且取得了意料之外的收获。"
        elif percent > 1:
            check_info += "失败了。"
        elif percent >= 1 / 2:
            if level_mapping[difficulty] > 1:
                check_info += "未达到所需级别，失败了。"
            else:
                check_info += "普通成功，完成了目标。"
        elif percent >= 1 / 5:
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
        python_code = self._check_agent(prompt)["content"]
        check_result = None
        if "`" in python_code:
            python_code = "\n".join([line for line in python_code.split("\n") if not line.startswith("`")])
        try:
            check_result = eval(python_code)
        except Exception as e:
            logger.exception(e)
            logger.error(f"尝试执行以下python代码失败：{python_code}")
        self._check_agent.memory.clear()
        return check_result

    def do_not_need_check(self, character_name: str):
        logger.info(f"{character_name}的行动不需要进行检定。")

    def impossible_check(self, character_name: str):
        logger.info(f"{character_name}的行动不可能达成，无需进行检定。")

    def __call__(self, x: Msg):
        self._script_listener_agent.observe(x)
        return self._scene_manager_agent(x)

    def illustrate(self):
        scene_description = self._current_scene.get_panorama_prompt()
        outlook = "\n".join(
            [c.get_name() + "：" + c.get_look_prompt() for c in self._current_scene.get_character_list()])
        script = "\n".join([f"{m['name']}：{m['content']}" for m in self.get_script()][-4:])
        prompt = f"场景如下：\n{scene_description}\n人物外貌：{outlook} \n剧本如下：\n{script}\n\n"
        sd_agent_prompt = self._illustration_agent(prompt)
        sd_prompt = self._stable_diffusion_agent(sd_agent_prompt)
        rsp = ImageSynthesis.call(model=ImageSynthesis.Models.wanx_v1,
                                  prompt="anime, " + sd_prompt["content"],
                                  n=1,
                                  size='1024*1024')
        if rsp.status_code == HTTPStatus.OK:
            # print(rsp.output)
            # print(rsp.usage)
            # save file to directory
            for result in rsp.output.results:
                file_name = PurePosixPath(unquote(urlparse(result.url).path)).parts[-1]
                with open(self._config_root_path + f"/images/{file_name}", 'wb+') as f:
                    f.write(requests.get(result.url).content)
                self._current_illustration_path = self._config_root_path + f"/images/{file_name}"
        else:
            logger.error('SDXL文生图失败, status_code: %s, code: %s, message: %s' %
                         (rsp.status_code, rsp.code, rsp.message))

    def get_illustration_path(self):
        return self._current_illustration_path
