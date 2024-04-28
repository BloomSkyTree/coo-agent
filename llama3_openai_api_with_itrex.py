from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from transformers import AutoTokenizer
from intel_extension_for_transformers.transformers import AutoModelForCausalLM

app = FastAPI()
model_path = "/data/modelscope/seanzhang/Llama3-Chinese"

model = AutoModelForCausalLM.from_pretrained(model_path, load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)


def format_messages_for_chatlm(messages):
    prompt = ""
    system_message = ""
    if messages and messages[0]['role'] == 'system':
        system_message = messages[0]['content']

    if system_message:
        prompt += '<|begin_of_text|>' + system_message

    for message in messages:
        content = message['content']
        if message['role'] == 'user':
            prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        elif message['role'] == 'assistant':
            prompt += f"{content}<|eot_id|>"

    return prompt


class RequestData(BaseModel):
    messages: List[str]
    max_new_tokens: int
    temperature: float


@app.post("/v1/chat/completions", response_model=str)
async def get_completions(data: RequestData):
    try:
        messages = data.messages
        max_new_tokens = data.max_new_tokens
        temperature = data.temperature

        # 使用第一个prompt进行生成
        prompt = format_messages_for_chatlm(messages)
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        current_length = len(input_ids[0])
        outputs = model.generate(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature
        )
        text = tokenizer.decode(outputs[0][current_length:], skip_special_tokens=True)

        return {
            "choices": [
                {
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": text,
                        "role": "assistant"
                    },
                    "logprobs": None
                }
            ],
            # "created": 1677664795,
            # "id": "chatcmpl-7QyqpwdfhqwajicIEznoc6Q47XAyW",
            "model": "llama3",
            "object": "chat.completion",
            "usage": {
                "completion_tokens": len(outputs[0][current_length:]),
                "prompt_tokens": len(input_ids),
                "total_tokens": len(outputs[0])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8787)
