import os

class DefaultConfig(dict):
    environ = os.environ
    # 当前目录是config目录
    CONFIG_PATH = os.path.dirname(__file__)
    # config目录所在目录就是项目的根目录
    PROJECT_PATH = os.path.dirname(CONFIG_PATH)
    BASE_DIR = os.path.abspath(PROJECT_PATH)

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@39.107.97.183:3306/aiss'
    # logger name
    # SQLALchemy配置
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False  # 每次请求结束后都会自动提交数据库的变动
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # 开启跟踪
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 3


    SUPER_ADMIN = 'admin'

    JWT_SECRET_KEY = 'cc-api'

    CORS_ORIGINS = ['*']
    CORS_METHODS = ['POST', 'GET', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']
    CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']

    # ****** 上传配置
    UPLOAD_FOLDER = '/tmp/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'sql'}

    # ############################## flask start config ######################################
    HOST = '0.0.0.0'
    PORT = 6000

    # 是否允许控制台打印，默认不允许
    AI_PRINT_CONSOLE = False

    # 定时任务开关
    SCHEDULER_API_ENABLED = True
    JOBS = [
        {
            'id': 'reload_face_from_db',
            'func': 'schedul_task:reload_face_from_db',
            'args': '',
            'trigger': 'interval',
            'seconds': 3600
        }]


