#!/usr/bin/env python
# coding=utf-8

# @Time           : 2018-12-09 下午5:22
# @Author         : wuyunzhen
# @File           : tools.py
# @Product        : PyCharm
# @Docs           : 工具类
# @Source         :

import os
import json
from collections import defaultdict
from werkzeug.datastructures import ImmutableMultiDict
from flask import current_app
from functools import reduce
from datetime import datetime
import uuid
import xmltodict

environ = os.environ


def xmlFile2dict(file_path):
    with open(file_path) as fd:
        doc = xmltodict.parse(fd.read())
        return doc


def xmlStr2dict(xml_str):
    return xmltodict.parse(xml_str)


def cvt2dict(data=None):
    """
    将各种类型转成dict,by wuyunzhen
    """
    if not data is None :
        if check_json_format(data):
            data = json.loads(data)
        elif not isinstance(data, dict):
            if isinstance(data, object):
                data = obj2dict(data)
    return data


def check_json_format(raw_msg):
    """
    检查字符串是否是json格式,by wuyunzhen
    """
    if isinstance(raw_msg, str):  # 首先判断变量是否为字符串
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False



def obj2dict(obj):
    """
    复杂object对象转dict格式,by wuyunzhen
    """
    dd = {}
    # 展开它的属性，这里智能用__dict__，不能用dict()方法,wuyunzhen.zh,20181208
    # print(obj.__dict__)
    for m in obj.__dict__:
        if m[0] != "_":
            value = getattr(obj, m)
            if not callable(value):
                dd[m] = complexObj2json(value)
    return dd


def list2json(ll):
    res_list = []
    for item in ll:
        value = complexObj2json(item)
        res_list.append(value)
    return res_list


def dict2json(dd):
    res = {}
    for item in dd:
        res[item] = complexObj2json(dd[item])
    return res


# complex obj to json
# 复杂对象转换json对象 (dict、list)
def complexObj2json(obj):
    # list, set, tuple
    if isinstance(obj, (list, set, tuple)):
        return list2json(obj)
    # dict
    elif isinstance(obj, dict):
        return dict2json(obj)
    # 基本类型
    # int, long, basestring, bool, float
    elif obj == None or isinstance(obj, (int,  str, complex, float, bool)):
        return obj
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    # 用户自定义的类
    else:
        return obj2dict(obj)



def allowed_file(filename):
    """
    >> print allowed_file(abc.jpg)

    :param filename:
    :return:
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.get('ALLOWED_EXTENSIONS')


def open_file_to_iterable(file_path):
    with open(file_path) as f:
        for line in f:
            yield line


def get_file_bytes(file_path):
    def prod(x, y):
        return x + y

    return reduce(prod, [len(b) for b in open_file_to_iterable(file_path)])


def create_or_pass_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)


def relative_path(f):
    return os.path.realpath(f).replace(
        '\\', '.').replace(
        '/', '.').replace(
        current_app.get('PROJECT_PATH').replace(
            '\\', '.').replace(
            '/', '.'), '').lstrip(
        '.').rstrip(
        '.py').rstrip(
        '.pyc').rstrip(
        '.__init__')


def encapsulation_class(target_class, target_object, func_name_list):
    [setattr(target_class, func_name, getattr(target_object, func_name))
     for func_name in func_name_list
     if getattr(target_object, func_name, None)]


def encapsulation_func(target_class, func):
    assert callable(func)
    setattr(target_class, func.__name__, func)


def parser_properties(file_path):
    properties_data = defaultdict(str)
    with open(file_path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            line = line.rstrip('\n').replace(' ', '')
            if not line:
                continue
            key, value = tuple(line.rstrip('\n').split('='))
            if value.startswith('${') and value.endswith('}'):
                args = tuple(value.lstrip('${').rstrip('}').split(':'))
                value = environ.get(*args)

            properties_data[key] = value
    return properties_data


def ai_print(self, *args, sep=' ', end='\n', file=None):
    # 根据环境变量判断是否进行打印，默认不打印，系统在进行启动时设置环境变量，
    # 只在加载dev.py配置文件时打印, wuyunzhen 20181222
    if (os.environ.get('AI_PRINT_CONSOLE') or 'False') == 'True':
        print(self, *args, sep=sep, end=end, file=file)


def multi_dict_parser2dict(multi_dict):
    if not isinstance(multi_dict, ImmutableMultiDict):
        raise AssertionError('object type must be ImmutableMultiDict')
    return {k: multi_dict[k] for k in multi_dict}


def gen_uuid():
    return uuid.uuid4().hex

class ParserProperties(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.__file_data = parser_properties(self.file_path)

    @property
    def data(self):
        return self.__file_data

    def get(self, key):
        if key in self.data.keys():
            return self.data[key]




