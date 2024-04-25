import agentscope

model_configs = [
    {
        "config_name": "qwen-max",
        "model_type": "dashscope_chat",
        "model_name": "qwen-max",
        "api_url": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
        "api_key": "sk-d1c122e76c8a4d11b78b3734e48960c6",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "sk-d1c122e76c8a4d11b78b3734e48960c6"
        },
        "messages_key": "input"
    },
    {
        "config_name": "qwen-local",
        "model_type": "post_api",
        "model_name": "qwen-local",
        "api_url": "http://127.0.0.1:5000/api/generate",
        "headers": {
            "Content-Type": "application/json",
        },
        "messages_key": "messages"
    }
]
agentscope.init(model_configs=model_configs)
