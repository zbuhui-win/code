# coding=utf-8

'''
接口层
'''
from flask_restful import Resource
from common import (make_response, HttpStatus, get_argument, exeTime, AiException, AiErrorCode,ai_print,gen_uuid)
import logging.config
import apps.humanDetectApp.dao.video_conn_info as video_conn_dao
from apps.humanDetectApp.dao.video_conn_info import VideoConnInfo
logger = logging.getLogger()

class VideoConnInfoCtrl(Resource):

    @exeTime
    def post(self):
        ccbinsId = get_argument("ccbinsId", required=True, help='所属机构不能为空')
        indexCode = get_argument("indexCode", required=True, help='所属设备不能为空')
        status = get_argument("status", required=True, help='报警类型不能为空')
        cct_rcrd_inf = get_argument("cct_rcrd_inf", required=False)
        eqmt_id = get_argument("eqmt_id", required=False)
        use_width = get_argument("use_width", required=False)
        thresh = get_argument("thresh", required=False)
        time_step = get_argument("time_step", required=False)

        video_conn_info_po = VideoConnInfo()
        video_conn_info_po.id = gen_uuid()
        video_conn_info_po.ccbins_id = ccbinsId
        video_conn_info_po.cct_rcrd_inf = cct_rcrd_inf
        video_conn_info_po.eqmt_id = eqmt_id
        video_conn_info_po.index_code = indexCode
        video_conn_info_po.status = status
        video_conn_info_po.param1 = use_width
        video_conn_info_po.param2 = thresh
        video_conn_info_po.param3 = time_step
        video_conn_dao.add_record(video_conn_info_po)
        return make_response(status=HttpStatus.SUCCESS, data={"code": "success"})




