# coding=utf-8

'''
接口层
'''
import json
import pickle
from flask_restful import Resource
from common import (make_response, HttpStatus, get_argument, exeTime, AiException, AiErrorCode,ai_print,gen_uuid)
import logging.config
import numpy as np
from datetime import datetime
import time
import os
import cv2 as cv
import base64
import apps.humanDetectApp.dao.alarm_info_hk as alarm_hk_dao
from apps.humanDetectApp.dao.alarm_info_hk import AlarmInfoHk
logger = logging.getLogger()
from apps.humanDetectApp.human_detect_config import yaml_cfg

from flask import request

class HkAlarmCtrl(Resource):

    @exeTime
    def post(self):
        orgName = get_argument("orgName", required=True, help='所属机构不能为空')
        deviceName = get_argument("deviceName", required=True, help='所属设备不能为空')
        alarmType = get_argument("alarmType", required=True, help='报警类型不能为空')
        alarmLevel = get_argument("alarmLevel", required=True, help='报警等级不能为空')
        alarmTime = get_argument("alarmTime", required=True, help='报警时间不能为空')
        remark = get_argument("remark", required=False)
        # 转回img
        img = pickle.loads(eval(remark))



        # json_data = request.form['json_data']
        # dict_data = json.loads(json_data)
        # orgName =dict_data.get('orgName',-1)
        # deviceName =dict_data.get('deviceName',-1)
        # alarmType =dict_data.get('alarmType')
        # alarmLevel =dict_data.get('alarmLevel')
        # alarmTime =dict_data.get('alarmTime')

        # f = request.files['myfile']
        # x=f.read()
        # print('>>>',x)
        # with open('D:/image/b123.jpg', 'ab') as f:
        #     f.write(x)
        # for i in f:
        #     print('@@',type(i))
        #     with open('D:/image/a.jpg', 'ab') as f:
        #         f.write(i)

        # 告警类别 00 对应海康 人数超限：'131643', '单人异常', '131644', '多人异常'
        # 告警类别 01 对应海康 非法入侵：'131585', '跨域警戒线','131588', '区域入侵', '131586', '人员进入'
        if alarmType == '131643':
            alarmType = '00'
            vlt_err_alrm_inf = '单人异常'
        elif alarmType == '131644':
            alarmType = '00'
            vlt_err_alrm_inf = '多人异常'
        elif alarmType == '131585':
            alarmType = '01'
            vlt_err_alrm_inf = '跨域警戒线'
        elif alarmType == '131588':
            alarmType = '01'
            vlt_err_alrm_inf = '区域入侵'
        elif alarmType == '131586':
            alarmType = '01'
            vlt_err_alrm_inf = '人员进入'
        elif alarmType == '150002':
            alarmType = '01'
            vlt_err_alrm_inf = '非法人员入侵'
        else:
            raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021012)

        alarm_info_hk_po = AlarmInfoHk()
        alarm_info_hk_po.id = gen_uuid()
        alarm_info_hk_po.ccbins_id = orgName
        alarm_info_hk_po.eqmt_id = deviceName
        alarm_info_hk_po.bsn_cgycd = alarmType
        alarm_info_hk_po.vlt_err_alrm_inf = vlt_err_alrm_inf
        alarm_info_hk_po.alarm_level = alarmLevel
        alarm_info_hk_po.stdt_tm = datetime.strptime(alarmTime, '%Y%m%d %H:%M:%S')

        if remark and len(remark) > 0:
            try:
                cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
                folder_path = yaml_cfg.get('illegal_image_path_hk') + "/" + cur_date + '/' + orgName
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                img_path = (folder_path + "/" + alarm_info_hk_po.id + ".jpg")

                cv.imwrite('D:/image/ab.jpg', img)
                # f.save(img_path)
                alarm_info_hk_po.uploadfiletrgtrfullnm = img_path
            except Exception:
                logger.error("存储hk告警图片失败, " + alarmType + "," + vlt_err_alrm_inf + "," + alarmTime)
        alarm_hk_dao.add_record(alarm_info_hk_po)
        return make_response(status=HttpStatus.SUCCESS, data={"code": "success"})




