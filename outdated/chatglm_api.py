from flask import Flask, request, jsonify
from loguru import logger
from transformers import AutoTokenizer, AutoModelForCausalLM
from intel_extension_for_transformers.neural_chat import PipelineConfig, GenerationConfig
from intel_extension_for_transformers.neural_chat import build_chatbot
from intel_extension_for_transformers.neural_chat import plugins
from intel_extension_for_transformers.neural_chat.models.chatglm_model import ChatGlmModel

app = Flask(__name__)

# 定义模型和分词器路径
model_path = r"D:\BaiduNetdiskDownload\modelscope\ZhipuAI\chatglm2-6b"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
config = PipelineConfig(model_name_or_path=model_path)
chatbot: ChatGlmModel = build_chatbot(config)


def build_prompt(messages):
    prompt = ""
    ask = None
    for i, message in enumerate(messages):
        if ask is None:
            prompt += f"[Round {int(i / 2) + 1}]\n\n问：{message['content']}\n\n"
            ask = message['content']
        else:
            ask = None
            prompt += f"答：{message['content']}\n\n"
    prompt += "答："
    return prompt


# 定义路由和视图函数
@app.route('/api/generate', methods=['POST'])
def generate_response():
    # 获取请求数据
    data = request.json
    messages = data.get("messages")
    messages[-1]["role"] = "user"

    # 应用聊天模板
    text = build_prompt(messages)

    logger.info(f"输入：{text}")

    # 批量解码
    response = chatbot.chat(text, config=GenerationConfig(temperature=0.8))
    logger.info(f"输出：{response}")
    return jsonify({
        "text": response
    })


# 启动 Flask 应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
