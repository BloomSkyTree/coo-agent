import json
import os
from typing import List

from utils.llm.BaseLlm import BaseLlm
from utils.llm.LlmFactory import LlmFactory
from utils.llm.LlmMessage import LlmMessage


class StoryManager:
    _story_json_file_path: str
    _story: List[LlmMessage]
    _full_story: List[LlmMessage]
    _full_story_length: int
    _current_story_length: int
    _llm_model_name: str
    _story_summarize_llm: BaseLlm

    def __init__(self, story_json_file, llm_model_name="autodl-llama"):
        self._story_json_file_path = story_json_file
        self._story = []
        self._full_story = []
        self._full_story_length = 0
        self._current_story_length = 0
        if os.path.isfile(self._story_json_file_path):
            with open(self._story_json_file_path, "r", encoding="utf-8") as json_file:
                for llm_message_parameter in json.loads(json_file.read()):
                    self.add(LlmMessage(parameters=llm_message_parameter))
        self._llm_model_name = llm_model_name
        system_prompt = [
            LlmMessage(role="system", content="扮演故事概括助手。你将得到故事的剧本，阅读并概括剧本中故事的主要内容，并在200字以内概括。\n"
                                              "回答时，直接对故事内容进行概括，不允许回答多余的内容。")
        ]
        self._story_summarize_llm = LlmFactory.get_llm_by_model_name(llm_model_name, system_prompt)



    def add(self, message):
        message_length = len(message.role) + len(message.content)
        self._full_story.append(message)
        self._story.append(message)
        self._full_story_length += message_length
        self._current_story_length += message_length
        if self._current_story_length > 4000:
            self.try_story_summarize()

    def get_current_story(self):
        return self._story

    def get_current_story_as_text(self):
        text = ""
        for message in self._story:
            text += f"{message.role}：{message.content}\n"
        return text

    def try_story_summarize(self):
        text = self.get_current_story()
        self._story_summarize_llm.clear_memory()
        message = self._story_summarize_llm.chat(query=LlmMessage(content=text), max_new_tokens=512)
        message.role = "故事概要"
        self._story = [message]
        self._current_story_length = len(message.role) + len(message.content)

    def save(self):
        story_content = [m.to_dict() for m in self._story]
        with open(self._story_json_file_path, "w", encoding="utf-8") as story_json_file:
            story_json_file.write(json.dumps(story_content, ensure_ascii=False))



