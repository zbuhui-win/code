import cv2
import sys
import base64
import requests
# from keyframe import KeyFrame
import time
from json import dumps
import os
import json
import traceback
import uuid
url = "http://127.0.0.1:5000/hk/alarm"

class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        """
        只要检查到了是bytes类型的数据就把它转为str类型
        :param obj:
        :return:
        """
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)


headers = {'Content-Type': 'application/json'}
request_data = {
                "orgName": '11212',
                "deviceName": "deviceName",
                "alarmType": '131643',
                "alarmLevel": "01",
                "alarmTime": "20181223 01:46:30",
                "remark": 'http://www.xinhuanet.com/titlepic/112431/1124310412_1554086287035_title0h.jpg'
                # "remark": 'D:/image/1.jpg'
                }

try:
    # print(request_data)
    json_data = json.dumps(request_data,cls=MyEncoder)
    print('json_data',json_data)
    ret = requests.post(url, data=json_data,headers=headers)
    res_dict = json.loads(ret.text)
    print(res_dict)
    # print("文件名：%s,总人数:%s，人脸数：%s,非法人数:%s" % ('1', res_dict['data']['num'], res_dict['data']['face_num'], res_dict['data']['un_num']))
    if ret.status_code == 200 and res_dict.get('error_code') == 'YCEA4021000':
        print('外呼成功')
    else:
        print('响应失败')
except Exception as e:
    exstr = traceback.format_exc()
    print('register blueprint fail, {}, error stack:{}'.format(e, exstr))
    print('外呼失败')

print("done")