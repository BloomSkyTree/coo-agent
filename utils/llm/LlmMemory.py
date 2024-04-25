from copy import deepcopy
from typing import List

from utils.llm.LlmMessage import LlmMessage


class LlmMemory:
    _system_prompt: List[LlmMessage]
    _memory: List[LlmMessage]
    _system_role_name: str

    def __init__(self, system_prompt=None, memory=None, system_role_name="user"):
        if system_prompt is None:
            self._system_prompt = []
        else:
            self._system_prompt = system_prompt
        if memory is None:
            self._memory = []
        else:
            self._memory = memory
        self._system_role_name = system_role_name

    def append(self, message):
        self._memory.append(message)

    def pop(self):
        return self._memory.pop()

    def clear(self):
        self._memory = []

    def reset(self, new_system_prompt=None):
        self.clear()
        if new_system_prompt is not None:
            self._system_prompt = new_system_prompt

    def __len__(self):
        return len(self._memory)

    def __getitem__(self, index):
        return self._memory[index]

    def __setitem__(self, index, value):
        self._memory[index] = value

    def __delitem__(self, index):
        del self._memory[index]

    def __str__(self):
        return str(self._memory)

    def __repr__(self):
        return repr(self._memory)

    def __copy__(self):
        new_system_prompt = deepcopy(self._system_prompt)
        new_memory = deepcopy(self._memory)
        new_llm_memory = LlmMemory(new_system_prompt, new_memory, self._system_role_name)
        return new_llm_memory

    def to_message_list(self):
        return [message.to_dict(system_role_name=self._system_role_name) for message in self._system_prompt + self._memory]
