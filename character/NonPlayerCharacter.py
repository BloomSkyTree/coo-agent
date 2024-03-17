from character.BaseCharacter import BaseCharacter


class NonPlayerCharacter(BaseCharacter):
    def __init__(self,
                 name: str,
                 outlook: str,
                 **kwargs):
        super().__init__(name, outlook, **kwargs)

