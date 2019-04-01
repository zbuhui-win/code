#!/usr/bin/env python
# coding=utf-8

# @Time           : 2018-12-09 下午3:20
# @Author         : wuyunzhen
# @File           : response_utils.py
# @Product        : PyCharm
# @Docs           : 返回处理工具类
# @Source         :


import json
import time
from functools import wraps
from common import AiException
from flask import request, jsonify, abort
from flask.globals import current_app
from common.aierrorcode import AiErrorCode

class HttpStatus(object):
    SUCCESS = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    NOT_ALLOWED = 405
    SERVER_ERROR = 500


class HttpError(object):
    @classmethod
    def bad_request(cls, arg=None):
        if not arg:
            abort(HttpStatus.BAD_REQUEST)
        abort(HttpStatus.BAD_REQUEST, "Required parameter '{}' is not present".format(arg))

    @classmethod
    def not_found(cls, arg=None):
        if not arg:
            abort(HttpStatus.NOT_FOUND)
        abort(HttpStatus.NOT_FOUND, "{}".format(arg))

    @classmethod
    def not_allowed(cls, arg=None):
        if not arg:
            abort(HttpStatus.NOT_ALLOWED)
        abort(HttpStatus.NOT_ALLOWED, "{}".format(arg))


def make_response(status=HttpStatus.SUCCESS, e=None, data=None):
    from common import cvt2dict
    """
    构建返回值信息
    :param status: 状态码
    :param e:　　　 信息
    :param data:   数据
    :return:   json str data
    """
    error_code = AiErrorCode.YCEA4021000.name if (not e) else AiErrorCode.YCEA4021999.name
    message_str = AiErrorCode.YCEA4021000.value if (not e) else AiErrorCode.YCEA4021999.value

    # assert isinstance(status, int)
    if status in range(200, 300) and not e:
        error_code = AiErrorCode.YCEA4021000.name
        message_str = AiErrorCode.YCEA4021000.value
    if hasattr(e, 'message') and e.message:
        message_str = e.message
    elif hasattr(e, 'description') and e.description:
        message_str = e.description

    data = cvt2dict(data)

    if e and isinstance(e, AiException):
        message_str = e.message
        error_code = e.error

    return jsonify({
        'status': status,
        # 'timestamp': int(round(time.time() * 1000)),
        'time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        'data': data,
        'path': request.path,
        'method': request.method,
        'error_code': error_code,
        'message': ('%s' % message_str)
    })


def json_encoder(func):
    """
    python obj to json
    :param func:
    :return: json data
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)
        return current_app.response_class(json.dumps(data, indent=2), mimetype='application/json')

    return wrapper
