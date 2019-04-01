# coding=utf-8

'''
接口层
'''
from flask_restful import Resource
import numpy as np
import cv2
from common import (make_response, HttpStatus, get_argument, exeTime, AiException, AiErrorCode)
import base64
import logging.config
from flask import request
import os
import common.constants as constants
# from apps.humanDetectApp.singleton import humanDetectSrv
logger = logging.getLogger()


class HumanDetectCtrl(Resource):

    @exeTime
    def post(self):
        # path_flag, cv_image_list = self.__check_args()
        # detect_result = humanDetectSrv.humanDetect(request.json, cv_image_list, path_flag)
        # if detect_result and len(detect_result) == len(cv_image_list):
        #     data = self.__make_response_data(detect_result, request.json)
        #     return make_response(status=HttpStatus.SUCCESS, data=data)
        # else:
        #     raise AiException(error_code=AiErrorCode.YCEA4021010)

        return make_response(status=HttpStatus.SUCCESS, data=data)

    def __make_response_data(self, detect_result, req_data):
        # 返回结果
        atc_rgc_inf_grp = []
        data = {'atc_rgc_inf_grp': atc_rgc_inf_grp}
        for ret in detect_result:
            # 一张文件
            atc_rgc_inf = {'atch_id': 'asdf'}
            model_rgc_grp = []
            for type in req_data.get('model_type'):
                # 一个模型
                model_rgc = {'model_type': type}
                rgc_grp = []
                #一帧图片
                rgc = {'pcsg_sttm': req_data.get('txn_dt_tm'), 'pcsg_edtm': req_data.get('txn_dt_tm')}
                if type == constants.cons_mdtp_human_detect:
                    rgc['txn_rsltcmnt'] = ret[0]
                    model_rgc_grp.append(model_rgc)
                    pass
                elif type == constants.cons_mdtp_human_recg:
                    rgc['txn_rsltcmnt'] = ret[2]
                    model_rgc_grp.append(model_rgc)
                    pass
                rgc_grp.append(rgc)
                model_rgc['rgc_grp']=rgc_grp

                atc_rgc_inf['model_rgc_grp'] = model_rgc_grp
            atc_rgc_inf_grp.append(atc_rgc_inf)

        return data

    def __check_args(self):

        get_argument(constants.cons_request_appid, required=True, help='应用组件编号不能为空')
        get_argument(constants.cons_request_trace_id, required=True, help='全局追踪号不能为空')
        get_argument(constants.cons_request_content_type, required=True, help='文件类型不能为空')
        get_argument(constants.cons_request_function, required=True, help='功能不能为空')
        get_argument(constants.cons_request_ccbins_id, required=True, help='机构编号不能为空')
        model_type = get_argument(constants.cons_request_model_type, type=list, required=True, help='模型服务类型不能为空')

        if not model_type:
            raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021008)

        path_list = get_argument(constants.cons_request_paths, required=False)
        img_list = get_argument(constants.cons_request_imgs, required=False)
        cv_image_list = []
        # 从路径数组中读图
        path_flag = False
        if path_list:
            path_flag = True
            logger.debug('path字段非空，从路径信息' + ':'.join(path_list))
            for path in path_list:
                if os.path.isfile(path):
                    img = cv2.imread(path)
                    cv_image_list.append(img)
                else:
                    raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021002, path)
        # 如果路径数组为空，从base64数组中读图
        elif img_list:
            logger.debug('path字段为空，取base64图片')
            for base64_img in img_list:
                if base64_img:
                    img_data = base64.b64decode(base64_img)
                    # 转换为np数组
                    img_array = np.fromstring(img_data, np.uint8)
                    # 转换成opencv可用格式
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    cv_image_list.append(img)
                else:
                    raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021006)
        else:
            raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021007)
        return path_flag, cv_image_list











