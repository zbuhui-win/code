# coding=utf-8

'''
接口层
'''

from common import (make_response, HttpStatus,exeTime,get_argument)
import logging.config
import base64
import numpy as np
import cv2
import datetime
from flask_restful import Resource
from flask import current_app
from flask import request
logger = logging.getLogger()

class FaceDetect(Resource):
    @exeTime
    def post(self):
        ### print(request.__dict__)
        image_base64 = get_argument('image_base64', required=True, help='图片信息')

        # # 将base64转成文件
        img_data = base64.b64decode(image_base64)
        # 转换为np数组
        img_array = np.fromstring(img_data, np.uint8)
        # 转换成opencv可用格式
        img_data = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # ### print(image_base64)
        # img_data = np.asarray(image_base64)

        dir = current_app.config.get('BASE_DIR')

        path = dir + "/image/" + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')+".jpg"
        cv2.imwrite(path, img_data)

        return make_response(status=HttpStatus.SUCCESS)

