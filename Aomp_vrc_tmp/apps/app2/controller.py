# coding=utf-8

'''
接口层
'''

from flask import request
from common import (make_response, HttpStatus, AiException, AiFileNotExistsError, exeTime, get_argument, AiErrorCode)
import logging.config
from flask_restful import Resource
import requests
import json

logger = logging.getLogger()


class TestArgsGet(Resource):

    def get(self):
        name = get_argument('username', required=True, help='请输入用户名')
        password = get_argument('password', required=True, help='请输入密码')

        # Get请求也可通过如下方式获取参数
        # name = request.args.get('username', '')
        # password = request.args.get('password', '')
        logger.info("name:%s, password:%s" % (name, password))
        return make_response(status=HttpStatus.SUCCESS, data={"name": name,"password":password})

    @exeTime
    def post(self):
        name = get_argument('username', required=True, help='请输入用户名')
        password = get_argument('password', required=False, help='请输入密码')

        #也可直接通过rest.form来获取请求报文
        # name = request.form['username']
        # password = request.form['password']

        logger.info("name:%s, password:%s" % (name, password))
        return make_response(status=HttpStatus.SUCCESS,
                             data={"name": name, "password": password})


class TestException(Resource):

    def get(self):
        logger.error("my test")
        raise AiException()

    def post(self):
        raise AiFileNotExistsError
        logger.info("name:%s, password:%s" % (request.form['username'], request.form['password']))
        return make_response(status=HttpStatus.SUCCESS,
                             data={"name": request.form['username'], "password": request.form['password']})


class TestErrorCode(Resource):
    def get(self):
        # 什么参数都不传
        raise AiException()
    def patch(self):
        # 只传基本参数
        raise AiException(500, AiErrorCode.YCEA4021999)
    def delete(self):
        # 错误码包含参数，需要两个参数，但少传了参数
        raise AiException(500, AiErrorCode.YCEA4021002, 'd:')
    def post(self):
        # 错误码包含参数，需要两个参数，且传参正确
        raise AiException(500, AiErrorCode.YCEA4021002, '/home/ap', 'a.txt')
    def put(self):
        # 调用make_response
        return make_response(status=HttpStatus.SUCCESS)


class TestLog2(Resource):
    @exeTime
    def get(self):
        while True:
            logger.info("app1.testLog")
        return 'app1.testLog'


class TestOutbound(Resource):
    def get(self):
        city = get_argument('city', required=True, help='请输入城市')
        if city is None:
            city = '武汉'

        # 下面接口须连互联网，查天气的接口
        url = "https://www.sojson.com/open/api/weather/json.shtml"
        request_data = {"city": city}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        ret = requests.get(url, params=request_data,headers=headers)
        # ### ### print(ret.url)
        if ret.status_code == 200:
            result = json.loads(ret.text)
            return make_response(status=HttpStatus.SUCCESS,data=result)
        return make_response(status=HttpStatus.SERVER_ERROR)


