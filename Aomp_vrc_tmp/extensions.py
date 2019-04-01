from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler


cors = CORS()


db = SQLAlchemy()

scheduler = APScheduler()

template = {
    'swagger': '2.0',
    'info': {
        'title': 'API文档',
        'version': '0.0.1'
    },
    # 'securityDefinitions': {
    #     'Token': {
    #         'type': 'apiKey',
    #         'name': 'Authorization',
    #         'in': 'header',
    #         'description': 'Bearer <jwt>'
    #     }
    # }
}
# swagger = Swagger(template=template)
