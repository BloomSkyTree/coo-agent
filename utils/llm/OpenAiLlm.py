import os
from copy import deepcopy
from typing import List

import tiktoken
from loguru import logger

from utils.llm.BaseLlm import BaseLlm
from openai import OpenAI

from utils.llm.LlmMemory import LlmMemory
from utils.llm.LlmMessage import LlmMessage


class OpenAiLlm(BaseLlm):
    _api_key: str
    _model_name: str
    _base_url: str
    _client: OpenAI

    def __init__(self, api_key: str = "null", model_name: str = None, base_url=None, **kwargs):
        super().__init__(**kwargs)
        self._api_key = api_key
        self._model_name = model_name
        self._base_url = base_url
        self._client = OpenAI(api_key=self._api_key, base_url=base_url)

    def get_valid_generate_parameters(self, all_parameters):
        parameters = super().get_valid_generate_parameters(all_parameters)
        if "max_tokens" in all_parameters:
            parameters["max_tokens"] = all_parameters["max_tokens"]
        elif "max_new_tokens" in all_parameters:
            parameters["max_tokens"] = all_parameters["max_new_tokens"] + self._token_usage
        else:
            logger.warning("对OpenAI API的调用未设置max_tokens或max_new_tokens。可能导致无限生成问题，敬请注意。")
        if "response_format" in all_parameters:
            parameters["response_format"] = all_parameters["response_format"]
        return parameters

    def chat(self, **kwargs):
        query = kwargs.get("query", None)
        if query is not None:
            self._memory.append(query)

        response = self._client.chat.completions.create(
            model=self._model_name,
            messages=self._memory.to_message_list(),
            **self.get_valid_generate_parameters(kwargs)
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
        stream = self._client.chat.completions.create(
            model=self._model_name,
            messages=self._memory.to_message_list(),
            stream=True,
            **self.get_valid_generate_parameters(kwargs)
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
                    self._token_usage = self._count_memory_tokens()
                    logger.debug(f"流式消息结束，此时token数：{self._count_memory_tokens()}")
                else:
                    raise Exception(
                        f"系统预设以外的停止原因：{finish_reason}。这些原因属Open AI预设，但不应出现在本流程中。")

            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    def _count_memory_tokens(self, model_name=None):
        """Return the number of tokens used by a list of messages."""
        if model_name is None:
            model_name = self._model_name
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            logger.warning("未找到适配模型名的编码，将使用cl100k_base进行妥协计算...")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model_name in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model_name == "gpt-3.5-turbo-0301":
            # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_message = 4
            # if there's a name, the role is omitted
            tokens_per_name = -1
        elif "gpt-3.5-turbo" in model_name:
            # 目前使用对gpt-3.5-turbo系列使用gpt-3.5-turbo-0613的token数计算方式。如果接口更新，需及时更改。
            return self._count_memory_tokens("gpt-3.5-turbo-0613")
        elif "gpt-4" in model_name:
            # "目前使用对gpt-4系列使用gpt-4-0613的token数计算方式。如果接口更新，需及时更改。"
            return self._count_memory_tokens("gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model_name}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in self._memory.to_message_list():
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def __deepcopy__(self, memodict={}):
        return OpenAiLlm(self._api_key, model_name=self._model_name, base_url=self._base_url,
                         memory=deepcopy(self._memory),
                         token_usage=self._token_usage)


if __name__ == '__main__':
    # encoding = tiktoken.encoding_for_model("gpt-4")
    # tokens = encoding.encode("tiktoken is great!")
    os.chdir(r"D:\PycharmProjects\ring-literature")
    # os.environ['http_proxy'] = 'http://localhost:33210'
    # os.environ['https_proxy'] = 'https://localhost:33211'
    from configuration import PROJECT_GLOBAL_CONFIG

    # api_key = "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"
    llm = OpenAiLlm(api_key=PROJECT_GLOBAL_CONFIG["openai"]["api_key"],
                    model_name="gpt-4", base_url="http://db.ringdata.net:33210/v1")
    # for word_chunk in llm.stream_chat(query=LlmMessage(content="Say this is a test")):
    #     print(word_chunk, end="")
    print(llm.chat(query=LlmMessage(content="Say this is a test")))
