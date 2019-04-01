# SQLALCHEMY_DATABASE_URI = 'oracle+cx_oracle://scott:tiger@127.0.0.1:1521/sidname'
SQLALCHEMY_DATABASE_URI = 'oracle+cx_oracle://vrc:vrc@localhost:1521/orcl'
JWT_SECRET_KEY = 'flask_cc_api'

SQLALCHEMY_ECHO = False
AI_PRINT_CONSOLE = False
CORS_ORIGINS = ['*']
CORS_METHODS = ['POST', 'GET', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']
CORS_ALLOW_HEADERS = ['Authorization', 'Content-Type']
