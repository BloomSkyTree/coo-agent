import abc
import asyncio
from typing import Union, List

from loguru import logger

from utils.llm.LlmMemory import LlmMemory
from utils.llm.LlmMessage import LlmMessage


class BaseLlm:
    _token_usage: int
    _memory: LlmMemory

    def __init__(self, **kwargs):
        self._token_usage = kwargs.get("token_usage", 0)
        system_prompt = kwargs.get("system_prompt", [])
        if not isinstance(system_prompt, list):
            system_prompt = [system_prompt]

        if "memory" in kwargs:
            self._memory = kwargs.get("memory")
        else:
            self._memory = LlmMemory(system_prompt)

    def reset(self, new_system_prompt=None):
        self._token_usage = 0
        self._memory.reset(new_system_prompt)

    def clear_memory(self):
        self._memory.clear()

    @abc.abstractmethod
    def chat(self, **kwargs):
        pass

    @abc.abstractmethod
    def stream_chat(self, **kwargs):
        pass

    def get_valid_generate_parameters(self, all_parameters):
        parameters = {}
        if "temperature" in all_parameters:
            parameters["temperature"] = all_parameters["temperature"]
        if "top_k" in all_parameters:
            parameters["top_k"] = all_parameters["top_k"]
        if "penalty_score" in all_parameters:
            parameters["penalty_score"] = all_parameters["penalty_score"]
        return parameters

    async def async_chat(self, **kwargs):
        return await asyncio.to_thread(self.chat, **kwargs)

    def get_memory(self):
        return self._memory

    def add_memory(self, message: LlmMessage):
        self._memory.append(message)

    def add_token_usage(self, token_num: int):
        self._token_usage += token_num

    def get_token_usage(self):
        return self._token_usage

    def regenerate(self, **kwargs):
        self._memory.pop()
        return self.chat(**kwargs)

    def get_latest_response(self):
        return self._memory[-1]
