#!/usr/bin/env python
# coding=utf-8


import traceback
from common import (make_response, AiException,AiFileNotExistsError, AiJsonError, AiMySQLDataError)
from flask_restful import Api as BaseApi
from werkzeug.exceptions import HTTPException
import logging.config
logger = logging.getLogger()


class Api(BaseApi):
    """
        继承Api类，重写handle_error方法，实现自己的异常处理逻辑
        by wuyunzhen.zh  20181208
    """

    def __init__(self, app=None, prefix='',
                 default_mediatype='application/json', decorators=None,
                 catch_all_404s=True, serve_challenge_on_401=False,
                 url_part_order='bae', errors=None):
        super().__init__(app, prefix,
                         default_mediatype, decorators,
                         catch_all_404s, serve_challenge_on_401,
                         url_part_order, errors)

    def handle_error(self, exception):
        if (isinstance(exception, AiFileNotExistsError) or isinstance(exception, AiJsonError)) \
                or isinstance(exception, HTTPException) \
                or isinstance(exception, AiMySQLDataError) \
                or isinstance(exception, AiException) \
                or isinstance(exception, Exception):
            exstr = traceback.format_exc()
            logger.error('process error, {}, error stack:{}'.format(exception, exstr))
            return make_response(500, exception)
        logger.error(exception)
        return make_response(500, exception)
