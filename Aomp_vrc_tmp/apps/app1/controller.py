# coding=utf-8

"""
    Rest接口示例，by wuyunzhen.zh  20181208
"""

from common import (make_response, HttpStatus,xmlFile2dict,xmlStr2dict,exeTime,get_argument,AiException)
import logging.config
import os
from flask_restful import Resource
from flask import current_app
from  apps.app1.dao import users
from extensions import db
logger = logging.getLogger()


class TestObject(Resource):
    @exeTime
    def get(self):
        class OutVo(object):
            def __init__(self, code=None, error=None, message=None):
                self.code = '123'
                self.error = '123'
                self.message = '123'

        out = OutVo()
        return make_response(status=HttpStatus.SUCCESS, data=out)

    @exeTime
    def post(self):
        class ClassBase():
            def __init__(self, code=None, error=None, message=None):
                self.code = '123'
                self.error = {'key': 'value', 'key1': 'value1'}
                self.data = ['ClassBase1', 'ClassBase2']

        class Class1(object):
            def __init__(self, code=None, error=None, message=None):
                self.code = '123'
                self.error = {'key': 'value', 'key1': 'value1'}
                self.data = [ClassBase(), ClassBase()]

        class OutVo(object):
            def __init__(self, code=None, error=None, message=None):
                self.code = '123'
                self.error = {'key': 'value', 'key1': 'value1'}
                self.message = [1, 2, 3]
                self.data = [Class1(), Class1()]

        out = OutVo()
        return make_response(status=HttpStatus.SUCCESS, data=out)

    @exeTime
    def put(self):
        data = {'name': 123, 'password': 'pasdf'}
        return make_response(status=HttpStatus.SUCCESS, data=data)


    @exeTime
    def delete(self):
        data = '{"name": "123", "password":123}'
        return make_response(status=HttpStatus.SUCCESS, data=data)


class TestLog(Resource):
    @exeTime
    def get(self):
        while True:
            logger.info("app1.testLog")
        return 'app1.testLog'


class TestXml2Dict(Resource):
    @exeTime
    def get(self):
        dir = current_app.config.get('BASE_DIR')
        test_xml_2_dict = xmlFile2dict(os.path.join(dir, 'test/file.xml'))
        return make_response(status=HttpStatus.SUCCESS, data=test_xml_2_dict)

    @exeTime
    def post(self):
        xmlStr = """
        <student>
            <stid>10213</stid>
            <info>
                <name>name</name>
                <mail>xxx@xxx.com</mail>
                <sex>male</sex>
            </info>
            <course>
                <name>math</name>
                <score>90</score>
            </course>
            <course>
                <name>english</name>
                <score>88</score>
            </course>
        </student>
        """
        test_xml_2_dict = xmlStr2dict(xmlStr)
        return make_response(status=HttpStatus.SUCCESS, data=test_xml_2_dict)

class TestDb(Resource):

    def post(self):
        name = get_argument('username', required=True, help='请输入用户名')
        password = get_argument('password', required=False, help='请输入密码')
        email = get_argument('email', required=False, help='请输入邮箱')
        users.create_user(name,email,password)
        return make_response(status=HttpStatus.SUCCESS)

    def put(self):
        try:
            name = get_argument('username', required=True, help='请输入用户名')
            email = get_argument('email', required=False, help='请输入邮箱')
            user1 = users.User.query.filter_by(name).first()
            user1.name = email
            db.session.commit()
            return make_response(status=HttpStatus.SUCCESS)
        except:
            db.session.rollback()
            raise AiException()

    def get(self):
        email = get_argument('email')
        user = users.user_by_email(email)
        return make_response(status=HttpStatus.SUCCESS, data=user)
    def delete(self):
        return make_response(status=HttpStatus.SUCCESS, data={"123":"asdf"})

