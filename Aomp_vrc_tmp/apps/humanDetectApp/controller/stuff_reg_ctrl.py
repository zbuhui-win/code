# coding=utf-8

'''
接口层
'''
from flask_restful import Resource
import cv2
from common import (make_response, HttpStatus, get_argument, exeTime, AiException, AiErrorCode,ai_print)
import logging.config
from flask import request
import common.constants as constants
# from apps.humanDetectApp.singleton import humanRecognizeSrv
import os

logger = logging.getLogger()


class StuffRegCtrl(Resource):

    @exeTime
    def post(self):
        ccbins_id = get_argument(constants.cons_request_ccbins_id, required=True, help='机构编号不能为空')
        # 已改成后台自动定时读取人脸库信息
        # humanRecognizeSrv.reload_faces_by_ins(ccbins_id)
        return make_response(status=HttpStatus.SUCCESS)

    # @exeTime
    # def post(self):
    #     empe_infs = self.__check_args()
    #     for empe in empe_infs:
    #         emb = humanRecognizeSrv.mod_ins_stuff(empe)
    #         ai_print(emb)
    #         emb = emb.reshape(-1)
    #         # 将ndArray转byte，再将byte转字符串
    #         emb_list = emb.tolist()
    #         empe[constants.cons_response_rslt_cmnt] = ",".join(str(s) for s in emb_list)
    #     data = self.__make_response_data(request.json, empe_infs)
    #     return make_response(status=HttpStatus.SUCCESS, data=data)

    def __make_response_data(self, req_data, empe_infs):
        # 返回结果
        rslt_cmnt_grp = []
        data = {constants.cons_response_rslt_cmnt_grp: rslt_cmnt_grp}
        for ret in empe_infs:
            rslt_cmnt_grp.append({constants.cons_response_rslt_cmnt: ret[constants.cons_response_rslt_cmnt]})
        return data

    def __check_args(self):

        get_argument(constants.cons_request_appid, required=True, help='应用组件编号不能为空')
        get_argument(constants.cons_request_trace_id, required=True, help='全局追踪号不能为空')
        ccbins_id = get_argument(constants.cons_request_ccbins_id, required=True, help='机构编号不能为空')
        empe_Grp = get_argument(constants.cons_request_empe_Grp, type=list, required=True, help='人员信息不能为空')

        empe_infs = []
        for empe in empe_Grp:
            empe_inf = {}
            empe_inf[constants.cons_request_ccbins_id] = ccbins_id
            empe_inf[constants.cons_request_empe_id] = empe[constants.cons_request_empe_id]
            empe_inf[constants.cons_request_usr_nm] = empe[constants.cons_request_usr_nm]
            empe_inf[constants.cons_request_mnt_tp_cd] = empe[constants.cons_request_mnt_tp_cd]
            if os.path.isfile(empe[constants.cons_request_path]):
                empe_inf[constants.cons_request_img] = cv2.imread(empe[constants.cons_request_path])
            else:
                raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021002, empe[constants.cons_request_path])
            empe_infs.append(empe_inf)
        return empe_infs


class FaceFetureCtrl(Resource):

    @exeTime
    def post(self):
        path = get_argument(constants.cons_request_path, required=True, help='文件路径为空')
        if os.path.isfile(path):
            img = cv2.imread(path)
            # cv2.imwrite("src.jpg", img)
            # 将图象由OpenCv的BGR转成RGB格式，wuyunzhen.zh, 20190309
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # cv2.imwrite("rgb.jpg", img)
            tmp_embs = humanRecognizeSrv.get_embedding(img)
            if len(tmp_embs) > 0:
                logger.info("计算人脸特征:")
                emb = tmp_embs[0].reshape(-1)
                # 将ndArray转byte，再将byte转字符串
                emb_list = emb.tolist()
                data = ",".join(str(s) for s in emb_list)
                ai_print(data)
                return make_response(status=HttpStatus.SUCCESS, data={"rslt_cmnt": data})
            raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021009, path)
        else:
            raise AiException(HttpStatus.SERVER_ERROR, AiErrorCode.YCEA4021002, path)


    # 重新装载人脸数据库
    @exeTime
    def put(self):
        humanRecognizeSrv.schedule_task_reg_ins_stuff()
        return make_response(status=HttpStatus.SUCCESS)

    # 重新计算人脸库特征向量，并存入数据库
    @exeTime
    def patch(self):
        humanRecognizeSrv.re_compute_featrue_from_db()
        return make_response(status=HttpStatus.SUCCESS)

