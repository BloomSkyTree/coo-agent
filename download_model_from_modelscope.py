import os

# 设置环境变量
os.environ['MODELSCOPE_CACHE'] = r'E:\BaiduNetdiskDownload/modelscope'
from modelscope import snapshot_download
model_dir = snapshot_download("ZhipuAI/chatglm2-6b")
