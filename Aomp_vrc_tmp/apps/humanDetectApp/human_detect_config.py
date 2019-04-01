# coding=utf-8

import yaml
from easydict import EasyDict as edict

conf_file = 'apps/humanDetectApp/human_detect_config.yml'
yaml_cfg = None
with open(conf_file, 'r', encoding='UTF-8') as f:
    yaml_cfg = edict(yaml.load(f))

