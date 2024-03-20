from agentscope.agents import AgentBase


class NonCharacterPlayerAgent(AgentBase):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
