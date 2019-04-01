# coding=utf-8

from datetime import datetime
from extensions import db
from common import AiMySQLDataError, HttpStatus, ai_print, constants, gen_uuid
import logging.config

logger = logging.getLogger()


class OprtRcdInfo(db.Model):
    __tablename__ = 'OPRT_RCD_INFO'
    id = db.Column(db.String(36), default=gen_uuid, primary_key=True)
    ccbins_id = db.Column(db.String(9))
    eqmt_id = db.Column(db.String(20))
    orig_lgc_sn = db.Column(db.String(120))
    cct_rcrd_inf = db.Column(db.String(300))
    stdt_tm = db.Column(db.DateTime)
    result = db.Column(db.String(100))
    bsn_cgycd = db.Column(db.String(2))
    dtl_info = db.Column(db.String(3000))
    uploadfiletrgtrfullnm = db.Column(db.String(600))
    sys_evt_trace_id = db.Column(db.String(36))
    last_udt_dt_tm = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


def add_records(results, req_data):
    oprt_list = []
    for result in results:
        if result[0] != -1:
            oprtRcdInfo = OprtRcdInfo()
            oprtRcdInfo.sys_evt_trace_id = req_data.get(constants.cons_request_trace_id)
            oprtRcdInfo.ccbins_id = req_data.get(constants.cons_request_ccbins_id)
            # 0330版本要上两个人数统计摄像头，将设备编号默认写死成同一个
            # oprtRcdInfo.eqmt_id = req_data.get(constants.cons_request_eqmt_id)
            oprtRcdInfo.eqmt_id = '001056'
            oprtRcdInfo.orig_lgc_sn = req_data.get(constants.cons_request_orig_lgc_sn)
            oprtRcdInfo.cct_rcrd_inf = req_data.get(constants.cons_request_cct_rcrd_inf)
            stdt_tm_str = req_data.get(constants.cons_request_txn_dt_tm)
            oprtRcdInfo.stdt_tm = datetime.strptime(stdt_tm_str, '%Y%m%d %H:%M:%S')
            oprtRcdInfo.bsn_cgycd = constants.cons_mdtp_human_detect
            oprtRcdInfo.result = constants.cons_bsn_result_fail if result[4] else constants.cons_bsn_result_success
            oprtRcdInfo.dtl_info = result[0]
            oprtRcdInfo.id = gen_uuid()
            oprtRcdInfo.uploadfiletrgtrfullnm = result[3]
            oprt_list.append(oprtRcdInfo)
        if result[1] != -1:
            # 非法人员入侵检测
            oprtRcdInfo = OprtRcdInfo()
            oprtRcdInfo.sys_evt_trace_id = req_data.get(constants.cons_request_trace_id)
            oprtRcdInfo.ccbins_id = req_data.get(constants.cons_request_ccbins_id)
            oprtRcdInfo.eqmt_id = req_data.get(constants.cons_request_eqmt_id)
            oprtRcdInfo.orig_lgc_sn = req_data.get(constants.cons_request_orig_lgc_sn)
            oprtRcdInfo.cct_rcrd_inf = req_data.get(constants.cons_request_cct_rcrd_inf)
            stdt_tm_str = req_data.get(constants.cons_request_txn_dt_tm)
            oprtRcdInfo.stdt_tm = datetime.strptime(stdt_tm_str, '%Y%m%d %H:%M:%S')
            oprtRcdInfo.bsn_cgycd = constants.cons_mdtp_human_recg
            oprtRcdInfo.result = constants.cons_bsn_result_fail if result[5] else constants.cons_bsn_result_success
            oprtRcdInfo.dtl_info = result[1]
            oprtRcdInfo.id = gen_uuid()
            oprtRcdInfo.uploadfiletrgtrfullnm = result[3]
            oprt_list.append(oprtRcdInfo)
    if len(oprt_list) > 0:
        try:
            db.session.add_all(oprt_list)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise AiMySQLDataError(HttpStatus.SERVER_ERROR, message='操作数据库失败')
