import asyncio

from configuration import PROJECT_GLOBAL_CONFIG
from utils.llm.OpenBuddyLlamaOpenAiLlm import OpenBuddyLlamaOpenAiLlm
from utils.llm.OpenAiLlm import OpenAiLlm


class LlmFactory:

    @staticmethod
    def get_llm_by_model_name(model_name, system_prompt=None):
        if system_prompt is None:
            system_prompt = []
        model_name = model_name.lower()
        if "gpt" in model_name:
            return OpenAiLlm(
                api_key=PROJECT_GLOBAL_CONFIG["openai"]["api_key"],
                model_name=model_name,
                system_prompt=system_prompt
            )
        if "llama" in model_name:
            return OpenBuddyLlamaOpenAiLlm(api_key="dummy",
                                           model_name=PROJECT_GLOBAL_CONFIG["autodl_llama"]["model_name"],
                                           base_url=PROJECT_GLOBAL_CONFIG["autodl_llama"]["url"],
                                           system_prompt=system_prompt)
        raise Exception("模型名称未匹配到适当的实现类")

    @staticmethod
    async def async_get_llm_by_model_name(model_name, system_prompt=None):
        return await asyncio.to_thread(LlmFactory.get_llm_by_model_name, model_name, system_prompt)
