from typing import Optional

from agentscope.agents import DialogAgent
from agentscope.prompt import PromptType


class KeeperControlledAgent(DialogAgent):

    def __init__(
            self,
            name: str,
            sys_prompt: Optional[str] = None,
            model_config_name: str = None,
            use_memory: bool = True,
            memory_config: Optional[dict] = None,
            prompt_type: Optional[PromptType] = PromptType.LIST,
    ) -> None:
        """Initialize the dialog agent.

        Arguments:
            name (`str`):
                The name of the agent.
            sys_prompt (`Optional[str]`):
                The system prompt of the agent, which can be passed by args
                or hard-coded in the agent.
            model_config_name (`str`, defaults to None):
                The name of the model config, which is used to load model from
                configuration.
            use_memory (`bool`, defaults to `True`):
                Whether the agent has memory.
            memory_config (`Optional[dict]`):
                The config of memory.
            prompt_type (`Optional[PromptType]`, defaults to
            `PromptType.LIST`):
                The type of the prompt organization, chosen from
                `PromptType.LIST` or `PromptType.STRING`.
        """
        super().__init__(
            name=name,
            sys_prompt=sys_prompt,
            model_config_name=model_config_name,
            use_memory=use_memory,
            memory_config=memory_config,
            prompt_type=prompt_type
        )

    def discard_the_two_latest_messages(self):
        self.memory.delete([self.memory.size() - 1, self.memory.size() - 2])

    def retry(self, extra_prompt=""):
        prompt_message = self.memory.get_memory(2)[0]
        self.discard_the_two_latest_messages()
        if extra_prompt:
            prompt_message["content"] += f"\n此外，必须遵循以下要求：{extra_prompt}"

    def set_latest_message_content(self, new_content):
        message = self.memory.get_memory(1)[0]
        message["content"] = new_content
        self.memory.delete(self.memory.size())
        self.memory.add(message)
