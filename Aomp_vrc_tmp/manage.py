#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time           : 18-7-10 上午10:22
# @Author         : Tom.Lee
# @File           : manager.py
# @Product        : PyCharm
# @Docs           :
# @Source         :


from app import create_app

app = create_app()
if __name__ == '__main__':
        app.run(host = '0.0.0.0',port = 8081,threaded=True)

