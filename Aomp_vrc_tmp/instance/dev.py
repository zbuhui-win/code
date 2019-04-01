SQLALCHEMY_DATABASE_URI = 'oracle+cx_oracle://vrc:vrc@127.0.0.1:1521/vrc'
JWT_SECRET_KEY = 'flask_cc_api'

CORS_ORIGINS = ['*']
CORS_METHODS = ['POST', 'GET', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']
CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']
AI_PRINT_CONSOLE = False
