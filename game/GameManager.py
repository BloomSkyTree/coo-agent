import json
import os
import random
import re
import shutil
import uuid
from typing import Union, List, Dict

from characters.BaseCharacter import BaseCharacter
from game.StoryManager import StoryManager
from utils.file_system_utils import find_files_matching_pattern, file_exists
from utils.json_utils import extract_json
from loguru import logger
from characters.NonPlayerCharacter import NonPlayerCharacter
from characters.PlayerCharacter import PlayerCharacter
from scene.Scene import Scene
from utils.llm.BaseLlm import BaseLlm
from utils.llm.LlmFactory import LlmFactory
from utils.llm.LlmMessage import LlmMessage
from utils.stable_diffusion_utils import draw
from utils.voicevox_utils import to_japanese_tts_and_save


class GameManager:
    _config_root_path: str
    _current_scene: Union[Scene, None]

    _panorama_agent: BaseLlm
    _illustration_agent: BaseLlm
    _character_outlook_agent: BaseLlm
    # _script_listener_agent: BaseLlm
    _scene_memory_agent: BaseLlm
    _if_check_agent: BaseLlm
    _check_detail_agent: BaseLlm
    _stable_diffusion_agent: BaseLlm
    _character_memory_agent: BaseLlm

    _current_illustration_path: Union[str, None]

    _player_check_info: List[str]
    _all_check_info: List[str]

    _characters: Dict[str, BaseCharacter]
    _story_manager: StoryManager

    def __init__(self, config_root_path):
        self._config_root_path = config_root_path

        self._characters = {}

        self._panorama_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个场景描述助手。根据提供的场景信息和额外提示词，你需要为其生成洛夫·克拉夫特风格的"
                            "画面描述。但是，别提到洛夫·克拉夫特。"
                            "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                            "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                            "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。"
                            "如果没有提及登场人物，则只描写景色。")
            ]
        )

        self._illustration_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个画面描述助手。根据提供的场景信息和剧本信息，你需要为人物描述补充标签。"
                            "注意，你描述的信息、登场人物不应超出被提供的信息的范围；"
                            "你的描述应注重画面感,不需要说明年代和地点，不需要传递太多信息。"
                            "对登场人物的叙述仅限外表、动作、神态，不允许进行心理描写。"
                            "注意，Keeper相当于旁白，不是登场人物。")
            ]
        )

        self._stable_diffusion_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个画面总结助手，根据所提供的剧本信息，你需要用英文标签式的形式对剧本中角色的神态、表情、动作进行总结概括。"
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
                            "回答时，标签使用英文逗号分隔，只允许回答标签，不需要回答其他内容。")
            ]
        )

        self._character_outlook_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个人物形象描述助手。根据提供的人物信息，对人物的外表、神态进行描写。"
                            "注意，你描述的信息不应超出被提供的信息的范围，且不允许进行心理描写。"
                            "除非明确要求，否则不允许有褒贬之意。尽量简短、白描。"
                            "以“有一位”开头，开始你的叙述。")
            ]
        )

        # self._script_listener_agent = LlmFactory.get_llm_by_model_name(
        #     model_name="autodl-llama"
        # )
        self._story_manager = StoryManager(self._config_root_path + "/story.json")

        # if file_exists(self._config_root_path, "story.json"):
        #     with open(self._config_root_path + "/story.json", "r", encoding="utf-8") as story_json_file:
        #         story = json.loads(story_json_file.read())
        #         for message in story:
        #             self._script_listener_agent.add_memory(LlmMessage(parameters=message))

        self._if_check_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个检定判断器。根据剧本内容，你需要判断某一角色当前的行为是否需要进行检定，并以JSON格式回答。\n"
                            "如果该角色没有进行什么特别的行动，或其目标从常理来说即使不依赖特定技能也能达成，则不需要检定，返回：{\"need_check\": false, \"possible\":true}\n"
                            "如果该角色的目标从常理来无论如何都不可能达成，则不需要检定，回答：返回：{\"need_check\": false, \"possible\":false}\n"
                            "如果该角色的目标视其自身能力或技能而言可能成功也可能失败，则回答：返回：{\"need_check\": true, \"possible\":true}")
            ]
        )

        self._check_detail_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个检定判断器。根据剧本内容，你需要判断某一角色当前的行为需要进行何种检定，并以JSON格式回答。\n"
                            "你的回答必须包含以下两个字段：\n"
                            "skill_or_ability_name：需要进行检定的技能或能力的名称，类型为字符串，可选值包括：侦查、图书馆使用、聆听、闪避、斗殴、潜行、说服、话术、魅惑、恐吓、偷窃、神秘学、克苏鲁神话。\n"
                            "difficulty：角色行为成功难易度，类型为字符串，可选值包括：普通、困难、极难。\n"
                            "以下是技能或能力的适用场合：\n"
                            "侦查：尝试发现被隐藏起来的东西或线索，觉察常人难以意识到的异象时适用。\n"
                            "潜行：尝试主动地隐蔽自己的行迹、动静时使用。\n"
                            "聆听：尝试通过听力等非视觉感官获取情报时适用。\n"
                            "话术：尝试进行言语上的哄骗，欺骗以及误导时适用。\n"
                            "魅惑：尝试以个人魅力博取对方好感时适用。\n"
                            "神秘学：尝试运用神秘学知识时适用。\n"
                            "图书馆使用：尝试在图书馆中查找资料时适用。\n"
                            "闪避：尝试躲避攻击时适用。\n"
                            "斗殴：徒手格斗时适用。\n"
                            "说服：花费较长时间，尝试以理服人时适用。\n"
                            "恐吓：口头威胁时适用。\n"
                            "偷窃：偷窃东西时适用。\n"
                            "克苏鲁神话：思考跟克苏鲁神话相关的内容时适用。\n"
                            "力量：进行需要力气的活动时适用。\n"
                            "体质：考验身体能否承受极端环境因素或者病毒、毒素时适用。\n"
                            "敏捷：考验身体灵活、敏捷程度时适用。\n"
                            "智力：在回想、思考时适用。\n"
                            "教育：在考察仅有通过专门学校学习才能学会的知识时适用。\n"
                            "以下是困难级别相关的说明：\n"
                            "普通：具有对应的技能或能力，在正常发挥的情况下能办到。\n"
                            "困难：即使具有对应的技能或能力，也因为自身状态或环境的恶劣，使得达成的难度更上一层楼。\n"
                            "极难：对于常人来说，依赖本身技能或能力很难办到，需要超常发挥且运气极佳才能达成；又或者自身状态或环境极端恶劣，使得正常发挥几乎不可能。\n"
                            "例如，一个人在尝试讨好另一个人，取得另一个人的好印象，需要进行普通级别的魅惑检定，你应返回：{\"skill_or_ability_name\":\"魅惑\", \"difficulty\":\"普通\"}")
            ]
        )

        self._character_memory_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个角色回忆代理。根据剧本内容，你需要为指定的角色生成简短的回忆，包括物件的得失、人际关系的变动以及别的令人印象深刻的事。"
                            "生成回忆时，不需要对自身形象和周围景色进行描写，只需要关注发生的事情。用语尽量简短，且应为单行文本。"
                            "注意：剧本中的Keeper是旁白的别称，不要将其当做登场人物。"
                            "回答时，以第三人称视角和描述过去的口吻进行。只输出回忆内容，不允许回答任何多余的内容。"
                )
            ]
        )

        self._scene_memory_agent = LlmFactory.get_llm_by_model_name(
            model_name="autodl-llama",
            system_prompt=[
                LlmMessage(
                    role="system",
                    content="你是一个场景效应代理。根据剧本内容，你需要用一句话总结：在剧本的最新事件发生时，有什么在场地中留下了持久的效应。\n"
                            "效应不应涉及人物、角色，着重关注对环境造成的影响。\n"
                            "例如，一杯水的翻倒，带来的效应有：地面被水浸湿了。\n"
                            "例如，一个角色开枪击中另一个角色，带来的效应有：血溅得到处都是；一颗弹孔留在了受害者背后的墙上。\n"
                            "如果存在多个效应，用分号间隔开。"
                )
            ]
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
        # self._current_scene.add_listener("剧本管理器", self._script_listener_agent)
        logger.info(f"切换为场景：{scene_name}")

    def draw_a_panorama(self, *args, **kwargs):
        logger.info("开始描绘场景...")
        message = LlmMessage(name="user", content=self._current_scene.get_panorama_prompt())
        message = self._panorama_agent.chat(query=message, max_new_tokens=512)
        logger.info(f"场景描绘：{message.content}")
        self._story_manager.add(LlmMessage(role="场景", content=message.content))
        if file_exists(self._config_root_path + "/images", f"{self._current_scene.get_name()}.png"):
            self._story_manager.add(
                LlmMessage(role="场景", content=self._config_root_path + f"/images/{self._current_scene.get_name()}.png")
            )

    def generate_scene_memory(self, max_recall=1):
        script_slice = self._story_manager.get_current_story()[-max_recall:]
        script_slice_content = "剧本如下：\n"
        for message in script_slice:
            script_slice_content += f"{message.role}: {message.content}\n"
        self._scene_memory_agent.clear_memory()
        message = self._scene_memory_agent.chat(query=LlmMessage(content=script_slice_content), max_new_tokens=256)
        logger.info(script_slice_content)
        logger.info(f"{message.role}: {message.content}")
        if "无效应" not in message.content:
            logger.info(f"造成场地效应：{message.content}")
            self._current_scene.add_memory(message.content)
        else:
            logger.info("本次旁白没有造成场地效应。")

    def save(self):
        logger.debug("触发存档。")
        script_memory = self.get_script().to_message_list()
        with open(self._config_root_path + f"/story.json", "w", encoding="utf-8") as story_json_file:
            story_json_file.write(json.dumps(script_memory, ensure_ascii=False))

        script = "\n".join([f"{message.role}：{message.content}" for message in self.get_script()])
        for character_name, character in self._characters.items():
            logger.info(f"保存角色：{character_name}")
            query = LlmMessage(role="user", content=f"剧本如下：\n{script}\n请以{character.get_name()}的视角，生成回忆。")
            memory = self._character_memory_agent.chat(query=query).content
            character.add_memory(memory)
            character.save(self._config_root_path)
        if self._current_scene is not None:
            self._current_scene.save(self._config_root_path)

    def get_character(self, character_name):
        if not character_name:
            return None
        if character_name not in self._characters:
            character = self.load_character(character_name)
            if character is None:
                return None
            self._characters[character_name] = character
        return self._characters[character_name]

    def load_character(self, character_name):
        player_path = self._config_root_path + f"/characters/player_characters/{character_name}.yaml"
        npc_path = self._config_root_path + f"/characters/non_player_characters/{character_name}.yaml"
        if os.path.exists(player_path):
            character = PlayerCharacter(config_path=player_path)
            logger.info(f"加载玩家角色：{character_name}")
            return character
        elif os.path.exists(npc_path):
            character = NonPlayerCharacter(config_path=npc_path, llm_model_name="llama")
            logger.info(f"加载非玩家角色：{character_name}")
            return character
        else:
            return None

    def character_outlook(self, character_name: str):
        character = self.get_character(character_name)
        if character is None:
            logger.warning(f"无法找到名为{character_name}的玩家或非玩家角色。将不会描述其外貌。")
            return
        outlook_message = self._character_outlook_agent.chat(
            query=LlmMessage(content=self.get_character(character_name).get_outlook()),
            max_new_tokens=1024
        )
        self._story_manager.add(LlmMessage(role="人物管理器", content=outlook_message.content))

    def character_act(self, character_name: str, act: str):
        character = self.get_character(character_name)
        if character is None:
            logger.warning(f"无法找到名为{character_name}的玩家或非玩家角色。当前行动：{act}将会被忽略。")
            return
        check_result = self.judge_check(character_name, act)
        self._story_manager.add(LlmMessage(role="检定管理器", content=check_result))
        if isinstance(character, NonPlayerCharacter):
            if check_result is None:
                rp_message = character(self._story_manager, f"进行以下动作的角色扮演：{act}")
            else:
                rp_message = character(self._story_manager,
                    f"进行以下动作的角色扮演：{act}，且该动作的结果为：{check_result}\n注意，在扮演和描述时，不能直接说出成功与否。")
            if rp_message is not None:
                self._story_manager.add(LlmMessage(role=character_name, content=rp_message.content))
                if character.get_tts_name() is not None:
                    self._add_tts(character.get_tts_name(), rp_message.content)

    def player_role_play(self, player_name, role_play):
        rp_message = LlmMessage(role=player_name, content=role_play)
        self._story_manager.add(rp_message)
        character = self.get_character(player_name)
        if character.get_tts_name() is not None:
            self._add_tts(character.get_tts_name(), rp_message.content)
        self.judge_check(player_name, role_play)

    def get_script(self):
        memory = self._story_manager.get_current_story()
        return memory

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
        scene_description = self._current_scene.get_panorama_prompt() if self._current_scene else "暂无场景信息"
        script = self._story_manager.get_current_story_as_text() if len(self.get_script()) > 0 else "暂无"
        prompt = f"场景如下：\n{scene_description}\n剧本如下：\n{script}\n" \
                 f"{character} 尝试进行以下言行：{act}\n" \
                 f"根据以上信息，判断{character}是否需要进行检定，以JSON格式回答。"
        prompt_message = LlmMessage(role="check-judge agent", content=prompt)
        self._if_check_agent.clear_memory()
        check_result = None
        try:
            if_check = extract_json(self._if_check_agent.chat(query=prompt_message, max_new_tokens=128).content)
            if if_check["need_check"]:
                prompt = f"场景如下：\n{scene_description}\n剧本如下：\n{script}\n" \
                         f"{character} 尝试进行以下言行：{act}\n" \
                         f"根据以上信息，判断{character}是需要进行何种检定，检定为何种难度，以JSON格式回答。"
                prompt_message = LlmMessage(role="check-judge agent", content=prompt)
                self._check_detail_agent.clear_memory()
                check = extract_json(self._check_detail_agent.chat(query=prompt_message, max_new_tokens=128).content)
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

    def illustrate(self):
        if self._current_scene is not None:


            tags = [tag for tag in self._current_scene.get_stable_diffusion_tags()]
            for message in self._story_manager.get_current_story():
                if message.role in self._characters:
                    character = self.get_character(message.role)
                    character_tags = character.get_stable_diffusion_tags()
                    tags.extend(character_tags)
                    query = LlmMessage(role="user",
                                       content=f"剧本如下：\n{self._story_manager.get_current_story_as_text()}\n\n，"
                                               f"为{character.get_name()}提供神态、表情和动作方面的标签。")
                    extended_tags = self._stable_diffusion_agent.chat(query=query).content.split(",")
                    tags.extend(extended_tags)
            logger.info(f"使用以下tag进行文生图：{tags}")
            image = draw(",".join(tags))
            image_name = uuid.uuid4()
            image_path = self._config_root_path + f"/images/{image_name}.png"
            image.save(image_path)
            self._story_manager.add(LlmMessage(role="插图", content=image_path))

    def get_selectable_scenes(self):
        return [filename.replace(".yaml", "") for filename in
                find_files_matching_pattern(self._config_root_path + "/scenes", r".*\.yaml")]

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

    def get_selectable_player_characters(self):
        return [s.strip().replace(".yaml", "")
                for s in
                find_files_matching_pattern(self._config_root_path + "/characters/player_characters", ".*yaml")]

    def get_selectable_non_player_characters(self):
        return [s.strip().replace(".yaml", "")
                for s in
                find_files_matching_pattern(self._config_root_path + "/characters/non_player_characters", ".*yaml")]

    def get_selectable_character_ability_and_skill(self, character_name):
        character = self.get_character(character_name)
        if character is None:
            return []
        ability_and_skill = character.get_ability_and_skill()
        dataframe = []
        for key in ability_and_skill:
            dataframe.append([key, ability_and_skill[key]])
        return dataframe

    def submit_aside(self, aside_content):
        self._story_manager.add(LlmMessage(role="旁白", content=aside_content))
        self.generate_scene_memory()

    def _add_tts(self, tts_name, content):
        # 使用正则表达式搜索双引号中的内容
        match = re.search(r'“(.*)”', content)
        if match:
            result = match.group(1)
            wav_path = self._config_root_path + f"/tts_result/{str(uuid.uuid4())}.wav"
            to_japanese_tts_and_save(tts_name, result, wav_path)
            self._story_manager.add(LlmMessage(role="TTS", content=wav_path))
