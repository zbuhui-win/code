# AiFramwwork
人工智能AI python-flask项目框架


## 环境准备

### 创建Python虚拟环境

- 创建虚拟环境（依赖python3.6）

```
切换目录
cd  D:\code\Python\AiFramewrok
创建虚拟环境
virtualenv venv
若报错，则说明没安装virtualenv,先执行如下命令安装
pip3 install virtualenv
激活虚拟环境
source venv/bin/activate  或者 venv/Scripts/activate
```

- 导入依赖包

```
pip install -r ./requirements.txt
```

- 启动项目

```
python manage.py
```

## 框架结构

### app
**介绍**： apps为应用的主目录，根据功能在下面创建不同的包来独立管理，如app1、app2
 - app1 第1个功能模块
```
    models文件夹存放模型相关文件
    dao文件夹存放数据库操作相关文件
    controller.py文件夹存放蓝图接口
```
 - app2 第2个功能模块
```
    models文件夹存放模型相关文件
    dao文件夹存放数据库操作相关文件
    controller.py文件夹存放蓝图接口
```
 - urls 所有功能的restful url地址
```
    __init__.py自动注册蓝图信息，要求url地址文件必须形如*_urls.py
    app1_urls.py app1的url地址
    app2_urls.py app2的url地址
    也可将所有app的url写在一个文件里，集中管理
```
    
### common
**介绍**： 公共模块
```
    decorators.py，装饰器文件，addlog装饰器给方法加日志,exeTime给方法加执行时间
    extensions.py，第三方扩展文件，集中管理，包括数据库、redis缓存、cors等
    exceptions.py，异常处理工具类
    requests_utils.py，请求封装工具类
    response_utils.py，交易返回封装工具类
    interceptor.py，拦截器文件
    tools.py，小工具函数
```

## 模块介绍

### 蓝图——框架已实现，使用者无须关心
**介绍**： 通过一个app(flask 实例)挂载多个blueprint实例，将项目功能模块化

- 创建APP
```
文件：app.py
代码：
    app = Flask(__name__, instance_relative_config=True, instance_path=_default_instance_path)
```

- 创建并挂载蓝图
```
文件：apps/urls/__init__.py，该文件负责将所有形如*_urls.py的文件注册成蓝图
代码：
    def register_blueprint(app):
```

### 日志logging

- 配置文件(logger.ini)
    
    创建root、error、debug等多个logger，并配置该logger的最低输出级别level
    
    创建FileRotateFileHandler等多个handler
    
    创建simpleFormatter, multiLineFormatter等多个Formatter
    
    每个logger可以挂载一到多个handler对象
    
    每个handler对象可以设置输出格式Formatter、输出文件路径、文件切割配置等
    
    输出目录./log文件夹，须提前创建log文件夹
- 配置装载
```
    文件：app.py
    代码：
        log_config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logger.ini')
        logging.config.fileConfig(log_config_path)
```
- 使用方法
```
    取root looger，默认用这个就可以
    import logging.config
    logger = logging.getLogger()
    logger.error('test log error')
    logger.info('test log info')
    logger.debug('test log debug')
    取其他logger，一般用不到
    errorlogger = logging.getLogger('error')
    debuglogger = logging.getLogger('debug')
```

### 异常处理

- 主动抛异常(AiException类)
```
    见apps.app2.controller.TestException.get方法
    class TestException(Resource):
        def get(self):
            logger.error("my test")
            raise AiException()
```
- 通用异常捕获(common/interceptors.py、apps/\__init\__.py文件)
    
    @app.errorhandler，可拦截各种响应码
    
    def handle_error(self, exception)，该方法会拦截所有异常
    
    
```
    # 响应码拦截
    @app.errorhandler(400)
    def bad_request(e):
        logger.error(e)
        return make_response(400, e)
    
    # 异常捕获
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
```


### 拦截器

- 全局拦截
```
    文件：common/interceptors.py
    
    # 在处理请求前拦截
    @app.before_request
    def process_request():
        if request.method == 'GET':
            logger.info('req addr:[%s] req method:[%s] req param:[%s]' % (
                str(request.path), str(request.method), str(request.args)))
        else:
            logger.info('req addr:[%s] req method:[%s] req param:[%s]' % (
                str(request.path), str(request.method), str(request.form)))

    # 在处理请求后拦截
    @app.after_request
    def process_response(response):
        if request.method == 'GET':
            logger.info('req addr:[%s] req method:[%s] req param:[%s] response status: [%s] response data[%s]' % (
                str(request.path), str(request.method), str(request.args), response.status, str(response.data)))
        else:
            logger.info('req addr:[%s] req method:[%s] req param:[%s] response status: [%s] response data[%s]' % (
                str(request.path), str(request.method), str(request.form), response.status, str(response.data)))
        return response

```

### request/response封装

- request
```
    文件：common/requests_utils.py
    方法：get_argument 获取request参数，并增加校验功能
    示例：apps/app2/contorller.py/TestArgsGet
    
    def get(self):
        name = get_argument('username', required=True, help='请输入用户名')
        password = get_argument('password', required=True, help='请输入密码')
        
    def post(self):
        name = get_argument('username', required=True, help='请输入用户名')
        password = get_argument('password', required=False, help='请输入密码')

```

- response
```
    通过common.response.make_response方法封装返回报文。
    其中data支持dict对象、json字符串、用户自定义java对象。
    详情参考app.app1.controller里的test_complex_object、testdict、testjson
```

### 工具类示例

- 打印交易耗时exeTime
```
    文件：common/decorators.py
    方法：exeTime 打印交易耗时
    示例：apps/app2/contorller.py/TestArgsGet
    
    @exeTime    
    def post(self):
        name = get_argument('username', required=True, help='请输入用户名')
        password = get_argument('password', required=False, help='请输入密码')

```

- 在方法前后打印日志addlog
```
    文件：common/decorators.py
    方法：addlog 打印交在方法前后打印日志
    示例：app.py文件
    
    @addlog
    def create_app():
```

### 访问数据库

- 数据库操作
```
    文件：apps/app1/dao/users.py
    示例：apps/app1/contorller.py/TestDb
    
    class TestDb(Resource):
        def post(self):
            name = get_argument('username', required=True, help='请输入用户名')
            password = get_argument('password', required=False, help='请输入密码')
            email = get_argument('email', required=False, help='请输入邮箱')
            users.create_user(name,email,password)
            return make_response(status=HttpStatus.SUCCESS)

```

### 调用第三方Restful接口

- 外呼调用
```
    说明：采用requests包进行外联访问
    示例：apps/app2/contorller.py/TestOutbound
    
     # 下面接口须连互联网，查天气的接口
    url = "https://www.sojson.com/open/api/weather/json.shtml"
    request_data = {"city": city}
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    }
    ret = requests.get(url, params=request_data,headers=headers)

```


