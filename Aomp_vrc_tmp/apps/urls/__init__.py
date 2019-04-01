# coding=utf-8
"""
    自动注册蓝图，要求urls文件必须形如*_urls.py
    by wuyunzhen.zh  20181208
"""

import os
import importlib
import traceback
from flask import Blueprint
from flask_restful import Api
from .. import Api
import logging.config
logger = logging.getLogger()

def register_blueprint(app):

    for f in os.listdir(os.path.split(__file__)[0]):
        module_name, ext = os.path.splitext(f)
        if module_name.endswith('_urls') and ext == '.py':

            module_blueprint = Blueprint(module_name[:-5], module_name)
            module_api = Api(module_blueprint, catch_all_404s=True)

            try:
                module = importlib.import_module('.' + module_name, __package__)
            except Exception as err:
                exstr = traceback.format_exc()
                logger.error('process error, {}, error stack:{}'.format(err, exstr))
                os._exit(0)

            for i, url in enumerate(module.urls):
                if i % 2:
                    module_api.add_resource(module.urls[i], module.urls[i - 1])
            app.register_blueprint(module_blueprint)
#
# def register_blueprint(app):
#     api = Api(app)
#     for f in os.listdir(os.path.split(__file__)[0]):
#         module_name, ext = os.path.splitext(f)
#         if module_name.endswith('_urls') and ext == '.py':
#
#             module_blueprint = Blueprint(module_name[:-5], module_name)
#             try:
#                 module = importlib.import_module('.' + module_name, __package__)
#             except Exception as err:
#                 ### print(traceback.format_exc())
#                 os._exit(0)
#
#             for i, url in enumerate(module.urls):
#                 if i % 2:
#                     api.add_resource(module.urls[i], module.urls[i - 1])
#             app.register_blueprint(module_blueprint)
