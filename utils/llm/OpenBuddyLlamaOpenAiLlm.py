import os
from copy import deepcopy
from typing import List

import tiktoken
from loguru import logger

from utils.llm.BaseLlm import BaseLlm
from openai import OpenAI

from utils.llm.LlmMemory import LlmMemory
from utils.llm.LlmMessage import LlmMessage
from utils.llm.OpenAiLlm import OpenAiLlm


class OpenBuddyLlamaOpenAiLlm(OpenAiLlm):
    _api_key: str
    _model_name: str
    _base_url: str
    _client: OpenAI

    def __init__(self, api_key: str = "null", model_name: str = None, base_url=None, **kwargs):
        super().__init__(api_key, model_name, base_url, **kwargs)

        system_prompt = kwargs.get("system_prompt", [])
        if not isinstance(system_prompt, list):
            system_prompt = [system_prompt]

        if "memory" in kwargs:
            self._memory = kwargs.get("memory")
        else:
            self._memory = LlmMemory(system_prompt, system_role_name="system")

        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url
        self._client = OpenAI(api_key=self._api_key, base_url=base_url)

    def get_valid_generate_parameters(self, all_parameters: dict):
        parameters = {}
        extra_body = {}
        if "temperature" in all_parameters:
            parameters["temperature"] = all_parameters["temperature"]
        else:
            parameters["temperature"] = 0.8
        if "top_k" in all_parameters:
            parameters["top_k"] = all_parameters["top_k"]
        if "penalty_score" in all_parameters:
            parameters["penalty_score"] = all_parameters["penalty_score"]
        token_limit = 8192
        if "max_tokens" in all_parameters:
            parameters["max_tokens"] = all_parameters["max_tokens"] \
                if all_parameters["max_tokens"] < token_limit \
                else token_limit
        elif "max_new_tokens" in all_parameters:
            extra_body["max_new_tokens"] = all_parameters["max_new_tokens"]
        else:
            logger.warning("对LlamaOpenAI API的调用未设置max_tokens或max_new_tokens。可能导致无限生成问题，敬请注意。")
        if "top_p" in all_parameters:
            parameters["top_p"] = all_parameters["top_p"]
        else:
            parameters["top_p"] = 0.8
        # parameters["stop"] = ["<|endoftext|>", "<|im_end|>", "<|im_start|>", "<|eot_id|>", "<|"]
        return parameters, extra_body

    def chat(self, **kwargs):
        query = kwargs.get("query", None)
        if query is not None:
            self._memory.append(query)
        generation_parameters, extra_body = self.get_valid_generate_parameters(kwargs)
        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=self._memory.to_message_list(),
            extra_body=extra_body,
            **generation_parameters,
        )
        response_message = LlmMessage(role=response.choices[0].message.role,
                                      content=response.choices[0].message.content.strip())
        self._memory.append(response_message)
        self._token_usage = response.usage.total_tokens
        return response_message

    def stream_chat(self, **kwargs):
        query = kwargs.get("query", None)
        if query is not None:
            self._memory.append(query)
        full_content = ""
        generation_parameters, extra_body = self.get_valid_generate_parameters(kwargs)
        stream = self._client.chat.completions.create(
            model=self._model_name,
            messages=self._memory.to_message_list(),
            stream=True,
            extra_body=extra_body,
            **generation_parameters
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                full_content += content
            finish_reason = chunk.choices[0].finish_reason
            if finish_reason is not None:
                if finish_reason == "stop" or finish_reason == "length":
                    response_message = LlmMessage(role="assistant", content=full_content)
                    self._memory.append(response_message)
                    self._token_usage = self._count_memory_tokens("gpt-3.5-turbo-0613")
                    logger.debug(f"流式消息结束，此时token数：{self._token_usage}")
                else:
                    raise Exception(
                        f"系统预设以外的停止原因：{finish_reason}。这些原因属Open AI预设，但不应出现在本流程中。")

            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def __deepcopy__(self, memodict={}):
        return OpenBuddyLlamaOpenAiLlm(self._api_key, model_name=self._model_name, base_url=self._base_url,
                                       memory=deepcopy(self._memory),
                                       token_usage=self._token_usage)


if __name__ == '__main__':
    # encoding = tiktoken.encoding_for_model("gpt-4")
    # tokens = encoding.encode("tiktoken is great!")
    from configuration import PROJECT_GLOBAL_CONFIG

    # api_key = "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"
    llm = OpenBuddyLlamaOpenAiLlm(api_key=PROJECT_GLOBAL_CONFIG["openai"]["api_key"],
                                  model_name="llama3",
                                  base_url="http://region-9.autodl.pro:48034/v1/")
    # for word_chunk in llm.stream_chat(query=LlmMessage(content="Say this is a test")):
    #     print(word_chunk, end="")
    print(llm.chat(query=LlmMessage(content="Say this is a test")))
