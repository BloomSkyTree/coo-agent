import json
import os
import random
import shutil
from http import HTTPStatus
from pathlib import PurePosixPath
from typing import Union, List
from urllib.parse import unquote, urlparse

import requests
from dashscope import ImageSynthesis

from utils.json_utils import extract_jsons
from agentscope.message import Msg
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
    _if_check_agent: KeeperControlledAgent
    _check_detail_agent: KeeperControlledAgent
    _stable_diffusion_agent: KeeperControlledAgent
    _character_memory_agent: KeeperControlledAgent

    _current_illustration_path: Union[str, None]

    _player_check_info: List[str]
    _all_check_info: List[str]

    def __init__(self, config_root_path):
        self._config_root_path = config_root_path

        self._scene_manager_agent = KeeperControlledAgent(
            name="场景管理器",
            sys_prompt="你是一个智能场景管理器。根据接受到的输入类型不同，你需要进行不同的python代码执行。\n"
                       "输入有以下几种类型："
                       "进入、开启、启用场景：调用scene_manager.enter_scene(scene_name: str)方法。"
                       "对场景进行描绘、与周围的景物相关（人物外貌的描述不在此列）时：调用scene_manager.draw_a_panorama()方法。。\n"
                       "对场景本身或场景中的物件造成持久的影响、留下痕迹时：调用scene_manager.generate_scene_memory(full_command: str)\n"
                       "对场景进行归档、保存或存档时：调用scene_manager.save()\n"
                       "要求绘制即时插图时：调用scene_manager.illustrate()\n"
                       "对人物外貌进行描述时：调用scene_manager.character_outlook(character_name:str)方法。\n"
                       "描述一个人物在进行某一行动（登场不计入在内）时，调用scene_manager.character_act(character_name:str, act: str)方法，其中act字段应包含原始指令中对动作的详细描述。\n"
                       "决定调用时需要传入的参数（字符串），直接给出需要执行的python代码。除非命令中使用英文，否则参数字符串取值一般是中文。\n"
                       "根据情况不同，若同时满足上述的多种场合，需要进行多个方法调用。调用时，顺序与说明时的顺序一致，由上到下。"
                       "注意：你只能回答能直接由eval()执行的python代码，不能回答其他多余的内容。",
            model_config_name="qwen-local",
            use_memory=True
        )

        self._panorama_agent = KeeperControlledAgent(
            name="场景描述",
            sys_prompt="你是一个场景描述助手。根据提供的场景信息和额外提示词，你需要为其生成洛夫·克拉夫特风格的"
                       "画面描述。但是，别提到洛夫·克拉夫特。"
                       "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                       "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                       "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。"
                       "如果没有提及登场人物，则只描写景色。",
            model_config_name="qwen-local",
            use_memory=True
        )

        self._illustration_agent = KeeperControlledAgent(
            name="即时描述",
            sys_prompt="你是一个画面描述助手。根据提供的场景信息和剧本信息，你需要为人物描述补充标签。"
                       "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                       "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                       "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。"
                       "注意，Keeper相当于旁白，不是登场人物。",
            model_config_name="qwen-local",
            use_memory=True
        )

        self._stable_diffusion_agent = KeeperControlledAgent(
            name="stable diffusion agent",
            sys_prompt="你是一个画面总结助手，根据所提供的剧本信息，你需要用英文标签式的形式对剧本中角色的神态、表情、动作进行总结概括。"
                       "你有以下可选的神态、表情标签：smile,laughing,grin,teasing_smile,smug,naughty_face,"
                       "evil smile,crazy_smile,happy_tears,"
                       "tear,crying,crying_with_eyes_open,streaming_tears,teardrop,tearing_up,tears,wiping_tears,"
                       "frustrated,frustrated_brow,annoyed,anguish,sigh,gloom,disappointed,despair,"
                       "frown,furrowed_brow,disgust,disdain,contempt,angry,glaring,serious,screaming,shouting,"
                       "expressionless,sleepy,drunk,bored,thinking,lonely,blush,shy,embarrass,facepalm,flustered,"
                       "sweat,scared,endured_face,crazy,trembling,moaning,\n"
                       "你有以下可选的动作标签：standing,on stomach,kneeling,on_side,on_stomach,"
                       "leaning_to_the_side,fighting_stance,leaning_forward,afloat,lying,comforting,cuddling,"
                       "dancing,climbing,chasing,hitting,imagining,jumping,flying_kick,kicking,licking,painting,"
                       "reading,sing,showering,slashing,sleeping,smelling,smoking,"
                       "sneezing,yawning,hiding,walking,waking_up\n"
                       "回答时，标签使用英文逗号分隔，只允许回答标签，不需要回答其他内容。",
            model_config_name="qwen-local",
            use_memory=True
        )

        self._character_outlook_agent = KeeperControlledAgent(
            name="人物形象描述",
            sys_prompt="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、神态进行描写。"
                       "注意，你描述的信息不应超出被提供的信息的范围，且不允许进行心理描写。"
                       "除非明确要求，否则不允许有褒贬之意。尽量简短、白描。"
                       "以“有一位”开头，开始你的叙述。",
            model_config_name="qwen-local",
            use_memory=True
        )

        self._script_listener_agent = KeeperControlledAgent(
            name="script listener agent",
            sys_prompt="",
            model_config_name="qwen-local",
            use_memory=True
        )

        self._if_check_agent = KeeperControlledAgent(
            name="检定判断器",
            sys_prompt="你是一个检定判断器。根据剧本内容，你需要判断某一角色当前的行为是否需要进行检定，并以JSON格式回答。\n"
                       "如果该角色没有进行什么特别的行动，或其目标从常理来说即使不依赖特定技能也能达成，则不需要检定，返回：{\"need_check\": false, \"possible\":true}\n"
                       "如果该角色的目标从常理来无论如何都不可能达成，则不需要检定，回答：返回：{\"need_check\": false, \"possible\":false}\n"
                       "如果该角色的目标视其自身能力或技能而言可能成功也可能失败，则回答：返回：{\"need_check\": true, \"possible\":true}",
            model_config_name="qwen-local",
            use_memory=False
        )

        self._check_detail_agent = KeeperControlledAgent(
            name="检定级别判断器",
            sys_prompt="你是一个检定判断器。根据剧本内容，你需要判断某一角色当前的行为需要进行何种检定，并以JSON格式回答。\n"
                       "你的回答必须包含以下两个字段：\n"
                       "skill_or_ability_name：需要进行检定的技能或能力的名称，类型为字符串，可选值包括：侦查、图书馆使用、聆听、闪避、斗殴、潜行、说服、话术、魅惑、恐吓、偷窃、神秘学、克苏鲁神话。\n"
                       "difficulty：角色行为成功难易度，类型为字符串，可选值包括：普通、困难、极难。\n"
                       "为了防止误解，以下是一些有歧义的技能的定义：\n"
                       "侦查：这项技能允许使用者发现被隐藏起来的东西或线索，觉察常人难以意识到的异象。\n"
                       "潜行：这项技能在使用者尝试主动地隐蔽自己的行迹、动静时适用。\n"
                       "聆听：这项技能在使用者尝试通过听力等非视觉感官获取情报时适用。\n"
                       "话术：话术特别限定于言语上的哄骗，欺骗以及误导。\n"
                       "魅惑：魅惑允许通过许多形式来使用，包括肉体魅力、诱惑、奉承或是单纯令人感到温暖的人格魅力。魅惑可能可以被用于迫使某人进行特定的行动，但是不会是与个人日常举止完全相反的行为。\n"
                       "神秘学：这项技能反应了对神秘学知识的了解。\n"
                       "克苏鲁神话：这项技能反应了对非人类（洛夫克拉夫特的）克苏鲁神话的了解。\n"
                       "以下是困难级别相关的说明：\n"
                       "普通：具有对应的技能或能力，在正常发挥的情况下能办到。\n"
                       "困难：即使具有对应的技能或能力，也因为自身状态或环境的恶劣，使得达成的难度更上一层楼。\n"
                       "极难：对于常人来说，依赖本身技能或能力很难办到，需要超常发挥且运气极佳才能达成；又或者自身状态或环境极端恶劣，使得正常发挥几乎不可能。\n"
                       "例如，一个人在尝试讨好另一个人，取得另一个人的好印象，需要进行普通级别的魅惑检定，你应返回：{\"skill_or_ability_name\":\"魅惑\", \"difficulty\":\"普通\"}",
            model_config_name="qwen-local",
            use_memory=False
        )

        self._character_memory_agent = KeeperControlledAgent(
            name="角色回忆代理",
            sys_prompt="你是一个角色回忆代理。根据剧本内容，你需要为指定的角色生成简短的回忆，包括物件的得失、人际关系的变动以及别的令人印象深刻的事。"
                       "生成回忆时，不需要对自身形象和周围景色进行描写，只需要关注发生的事情。用语尽量简短，且应为单行文本。"
                       "注意：剧本中的Keeper是旁白的别称，不要将其当做登场人物。"
                       "回答时，以第三人称视角和描述过去的口吻进行。只输出回忆内容，不允许回答任何多余的内容。",

            model_config_name="qwen-local",
            use_memory=True
        )
        self._current_scene = None
        self._current_illustration_path = None
        self._player_check_info = []
        self._all_check_info = []

    def enter_scene(self, scene_name):
        if self._current_scene is not None:
            if scene_name == self._current_scene.get_name():
                logger.warning("将切换的场景为当前场景，不进行切换。")
                return
            self.save()
        scene_config_path = self._config_root_path + f"/scenes/{scene_name}.yaml"
        self._current_scene = Scene(config_path=scene_config_path)
        self._current_scene.add_listener(self._script_listener_agent)
        logger.info(f"切换为场景：{scene_name}")

    def draw_a_panorama(self, *args, **kwargs):
        message = Msg(name="panorama agent", content=self._current_scene.get_panorama_prompt())
        message = self._panorama_agent(message)
        self._script_listener_agent.observe(message)

    def generate_scene_memory(self, memory):
        self._current_scene.add_memory(memory)

    def save(self):
        script = "\n".join([f"{m['name']}：{m['content']}" for m in self.get_script()])
        for character in self._current_scene.get_character_list():
            memory = self._character_memory_agent(f"剧本如下：\n{script}\n请以{character.get_name()}的视角，生成回忆。")["content"]
            character.add_memory(memory)
        self._current_scene.save(self._config_root_path)

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
        message = Msg(name="outlook prompt", content=self._current_scene.get_character(character_name).get_outlook())
        outlook_message = self._character_outlook_agent(
            message
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
            if check_result is not None:
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
        if isinstance(character, PlayerCharacter):
            self._player_check_info.append(check_info)
        self._all_check_info.append(check_info)
        return check_info

    def judge_check(self, character, act):
        scene_description = self._current_scene.get_panorama_prompt()
        script = "\n".join([f"{m['name']}：{m['content']}" for m in self.get_script()]) if len(
            self.get_script()) > 0 else "暂无"
        prompt = f"场景如下：\n{scene_description}\n剧本如下：\n{script}\n" \
                 f"{character} 尝试进行以下言行：{act}\n" \
                 f"根据以上信息，判断{character}是否需要进行检定，以JSON格式回答。"
        prompt_message = Msg(name="check-judge agent", content=prompt)

        check_result = None
        try:
            if_check = extract_jsons(self._if_check_agent(prompt_message)["content"])[0]
            if if_check["need_check"]:
                prompt = f"场景如下：\n{scene_description}\n剧本如下：\n{script}\n" \
                         f"{character} 尝试进行以下言行：{act}\n" \
                         f"根据以上信息，判断{character}是需要进行何种检定，检定为何种难度，以JSON格式回答。"
                prompt_message = Msg(name="check-judge agent", content=prompt)
                check = extract_jsons(self._check_detail_agent(prompt_message)["content"])[0]
                return self.do_check(character, check["skill_or_ability_name"], check["difficulty"])
            else:
                if if_check["possible"]:
                    return "不需要检定，直接成功。"
                else:
                    return "不可能成功。"
        except Exception as e:
            logger.exception(e)
        return check_result

    def do_not_need_check(self, character_name: str):
        logger.info(f"{character_name}的行动不需要进行检定。")

    def impossible_check(self, character_name: str):
        logger.info(f"{character_name}的行动不可能达成，无需进行检定。")

    def __call__(self, x: Msg):
        self._script_listener_agent.observe(x)
        # return self._scene_manager_agent(x)

    def illustrate(self):

        script = "\n".join([f"{m['name']}：{m['content']}" for m in self.get_script()])
        tags = [tag for tag in self._current_scene.get_stable_diffusion_tags()]
        for character in self._current_scene.get_character_list():
            character_tags = character.get_stable_diffusion_tags()
            tags.extend(character_tags)
            prompt = f"剧本如下：\n{script}\n\n，为{character.get_name()}提供神态、表情和动作方面的标签。"
            extended_tags = self._stable_diffusion_agent(prompt)["content"].split(",")
            tags.extend(extended_tags)
        logger.info(f"使用以下tag进行文生图：{tags}")
        rsp = ImageSynthesis.call(model=ImageSynthesis.Models.wanx_v1,
                                  prompt=",".join(tags),
                                  n=1,
                                  size='1024*1024')
        if rsp.status_code == HTTPStatus.OK:
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

    def get_player_check_info(self):
        return self._player_check_info

    def get_all_check_info(self):
        return self._all_check_info

    def reset(self):
        if os.path.exists(self._config_root_path):
            shutil.rmtree(self._config_root_path)
            # 复制resources文件夹的内容到self._config_root_path
            resources_path = os.path.join(os.getcwd(), 'resources')
            shutil.copytree(resources_path, self._config_root_path)
