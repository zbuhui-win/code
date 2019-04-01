#!/usr/bin/env python
# coding=utf-8

# @Time           : 2018-12-09 下午3:13
# @Author         : wuyunzhen
# @File           : interceptors.py
# @Product        : PyCharm
# @Docs           : 拦截器类
# @Source         :

from common import (make_response,addlog)
import traceback
import logging.config
from flask import request
import copy
import common.constants as constants
logger = logging.getLogger()
errorlogger = logging.getLogger('error')
debuglogger = logging.getLogger('debug')


@addlog
def configure_errorhandler(app):
    # @app.before_request
    # def process_request():
    #     if request.method == 'GET':
    #         logger.info('req addr:[%s] req method:[%s] req param:[%s]' % (
    #             str(request.path), str(request.method), str(request.args)))
    #     else:
    #         request_param = request.json
    #         tmp_request_param = copy.deepcopy(request_param)
    #         # 不展示图片base64，其他均展示
    #         if request_param.get(constants.cons_request_imgs):
    #             tmp_request_param[constants.cons_request_imgs] = []
    #         if request_param.get('remark'):
    #             tmp_request_param['remark'] = []
    #         logger.info('req addr:[%s] req method:[%s] req param:[%s]' % (
    #             str(request.path), str(request.method), str(tmp_request_param)))
    #
    # @app.after_request
    # def process_response(response):
    #
    #     # 返回报文，只打印status、appid、sys_evt_trace_id以及返回体
    #     if request.method == 'GET':
    #         appid = request.args.get(constants.cons_request_appid)
    #         sys_evt_trace_id = request.args.get(constants.cons_request_trace_id)
    #     else:
    #         request_param = request.json
    #         appid = request_param.get(constants.cons_request_appid)
    #         sys_evt_trace_id = request_param.get(constants.cons_request_trace_id)
    #     logger.info(
    #         '{sys_evt_trace_id: [%s]} ----- {response status: [%s] response data[%s]}' % (
    #             sys_evt_trace_id, response.status,
    #             str(response.data)))
    #     return response

    @app.errorhandler(400)
    def bad_request(e):
        logger.error(e)
        return make_response(400, e)

    @app.errorhandler(401)
    def unauthorized(e):
        logger.error(e)
        return make_response(401, e)

    @app.errorhandler(403)
    def forbidden(e):
        return make_response(403, e)

    @app.errorhandler(404)
    def not_found(e):
        logger.error(e)
        return make_response(404, e)

    @app.errorhandler(405)
    def not_allowed(e):
        logger.error(e)
        return make_response(405, e)

    @app.errorhandler(502)
    def bad_gateway(e):
        exstr = traceback.format_exc()
        errorlogger.error('register blueprint fail, {}, error stack:{}'.format(e, exstr))
        debuglogger.error('register blueprint fail, {}, error stack:{}'.format(e, exstr))
        return make_response(502, e)

    @app.errorhandler(503)
    def service_unavailable(e):
        logger.error(e)
        return make_response(503, e)

    @app.errorhandler(504)
    def bad_gateway_timeout(e):
        logger.error(e)
        return make_response(504, e)

    # 拦截指定响应码
    @app.errorhandler(500)
    def server_error(e):
        logger.error(e)
        return make_response(500, e)

    # 此处定义的异常拦截器不好使，须在 apps.__init__.py文件里handle_error方法里定义异常处理模块，
    # 具体原因不清楚，暂时注视掉该代码,wuyunzhen.zh,20181208
    # # 拦截自定义AiException
    # @app.errorhandler(AiException)
    # def my_exception(e):
    #     exstr = traceback.format_exc()
    #     logger.error('register blueprint fail, {}, error stack:{}'.format(e, exstr))
    #     return make_response(500, e)
    #
    #
    # # 拦截全局Exception
    # @app.errorhandler(Exception)
    # def server_exception(e):
    #     exstr = traceback.format_exc()
    #     logger.error('register blueprint fail, {}, error stack:{}'.format(e, exstr))
    #     return make_response(500, e)

