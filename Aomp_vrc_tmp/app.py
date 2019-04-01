import os
from flask import Flask
from apps import urls
from config.default_config import DefaultConfig
# from extensions import (cors, db, scheduler)
from extensions import (cors, scheduler)
import logging.config
from common import configure_errorhandler,addlog,ai_print
import logging.config
import traceback
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'
log_config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logger.ini')
logging.config.fileConfig(log_config_path)
logger = logging.getLogger()

_default_instance_path = '%(instance_path)s/instance' % \
                         {'instance_path': os.path.dirname(os.path.realpath(__file__))}


# 方法不起作用，具体原因不清楚，注视掉,wuyunzhen.zh,20181208
# def log_exception(sender, exception, **extra):
#     if (isinstance(exception, AiFileNotExistsError) or isinstance(exception, AiJsonError)) \
#             or isinstance(exception, HTTPException) \
#             or isinstance(exception, AiMySQLDataError) \
#             or isinstance(exception, AiException) \
#             or isinstance(exception, Exception):
#
#         exstr = traceback.format_exc()
#         logger.error('register blueprint fail, {}, error stack:{}'.format(exception, exstr))
#         return make_response(500, exception)
#     logger.error(exception)
#     return make_response(500, exception)

@addlog
def create_app():
    app = Flask(__name__, instance_relative_config=True, instance_path=_default_instance_path)
    try:
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
        configure_app(app)
        configure_extensions(app)
        configure_blueprint(app)
        configure_errorhandler(app)
        # configure_logging(app)
        return app
    except Exception as e:
        exstr = traceback.format_exc()
        logger.error('process error, {}, error stack:{}'.format(e, exstr))
        os._exit(0)

@addlog
def configure_app(app):
    app.config.from_object(DefaultConfig)
    run_env = os.environ.get('RUN_ENV') or 'prod.py'
    app.config.from_pyfile(run_env)

    # 配置ai_print方法是否生效的环境变量
    AI_PRINT_CONSOLE = 'False'
    if app.config.get('AI_PRINT_CONSOLE'):
        AI_PRINT_CONSOLE = 'True'
    os.environ['AI_PRINT_CONSOLE'] = AI_PRINT_CONSOLE




@addlog
def configure_extensions(app):

    # cors
    cors.init_app(app,
                  origins=app.config['CORS_ORIGINS'],
                  methods=app.config['CORS_METHODS'],
                  allow_headers=app.config['CORS_ALLOW_HEADERS'])
    # db
    # db.init_app(app)
    # swagger
    # swagger.init_app(app)

    # 从数据库加载人脸基本信息
    # from apps.humanDetectApp.dao.read_face_from_db import read_from_db
    # read_from_db.read_db(app)

    # scheduler定时任务
    # scheduler.init_app(app)

    # scheduler.start()


# def configure_logging(app):
#     got_request_exception.connect(log_exception, app)

@addlog
def configure_blueprint(app):
    urls.register_blueprint(app)
