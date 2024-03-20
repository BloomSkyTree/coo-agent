from typing import List


class ScriptManager:
    _scripts: List[str]

    def __init__(self):
        self._scripts = []

    def add_script(self, script):
        self._scripts.append(script)

    def get_all_scripts(self):
        return "\n".join(self._scripts)





