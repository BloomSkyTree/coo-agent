from typing import List

from agents.KeeperControlledAgent import KeeperControlledAgent


class ScriptManager:
    _scripts: List[str]
    _agent: KeeperControlledAgent

    def __init__(self):
        self._scripts = []

    def __call__(self, *args, **kwargs):
        self._agent(*args, **kwargs)
    def to_script(self):
        return [message["content"] for message in self._agent.memory]



