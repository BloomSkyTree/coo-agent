from typing import Dict

import yaml
from agentscope.agents import UserAgent

from characters.BaseCharacter import BaseCharacter


class PlayerCharacter(BaseCharacter):
    _agent: UserAgent


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._agent = UserAgent()

    def __call__(self, *args, **kwargs):
        self._agent(*args, **kwargs)

    def get_agent(self):
        return self._agent


