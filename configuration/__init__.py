# -*- coding: utf-8 -*-
"""
@File       : __init__.py.py
@Author     : Yuka
@Time       : 2021/9/28 10:17
@Version    : 1.0.0
@Description: 
"""
import json

import yaml

with open("configs/config.yaml", "r", encoding="utf-8") as base_config_file:
    base_config = yaml.load(base_config_file, Loader=yaml.FullLoader)
if "sub_config" in base_config:
    for sub_config_file_name in base_config["sub_config"]:
        with open("configs/{}.yaml".format(sub_config_file_name), "r", encoding="utf-8") as sub_config_file:
            sub_config = yaml.load(sub_config_file, Loader=yaml.FullLoader)
            for key in sub_config:
                base_config[key] = sub_config[key]

PROJECT_GLOBAL_CONFIG = base_config
