import json
import re


def extract_jsons(input_string):
    # 使用正则表达式提取字符串中的所有JSON结构
    json_patterns = re.compile(r'\{[^{}]*\}')
    json_strings = json_patterns.findall(input_string)

    # 将提取的字符串转换为JSON对象
    extracted_jsons = [json.loads(json_str) for json_str in json_strings]

    return extracted_jsons