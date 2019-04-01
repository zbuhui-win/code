#!/usr/bin/env python
# coding=utf-8

# @Time           : 2018-12-09 下午3:13
# @Author         : wuyunzhen
# @File           : exceptions.py
# @Product        : PyCharm
# @Docs           : 
# @Source         : 

from common.aierrorcode import AiErrorCode


class AiException(Exception):
    code = 500  # 存放HTTP状态
    error = AiErrorCode.YCEA4021999.name  # 存放错误码，没有异常时为000000000，异常时形如YCEA0421q001
    message = AiErrorCode.YCEA4021999.value  # 存放错误信息
    params = {}

    def __init__(self, code=500, error_code=AiErrorCode.YCEA4021999, *params):
        self.code = self.__class__.code if not code else code
        self.error = self.__class__.error if not error_code.name else error_code.name
        self.message = self.__class__.message if not error_code.value else error_code.value
        self.params = self.__class__.params if not params else params
        # 错误码参数替换
        if self.params:
            for param in self.params:
                self.message = self.message.replace("@@{}@@", param, 1)

    def __str__(self):
        return '<{}>: {}'.format(self.__class__.__name__, self.message)

    # @property
    # def code(self):
    #     return self.code
    #
    # @property
    # def error(self):
    #     return self.error
    #
    # @property
    # def message(self):
    #     return self.message


class AiFileNotExistsError(AiException):
    code = 500
    error = AiErrorCode.YCEA4021001.name
    message = AiErrorCode.YCEA4021001.value


class AiJsonError(AiException):
    code = 500
    error = AiErrorCode.YCEA4021003.name
    message = AiErrorCode.YCEA4021003.value


class AiMySQLDataError(AiException):
    code = 500
    error = AiErrorCode.YCEA4021004.name
    message = AiErrorCode.YCEA4021004.value
