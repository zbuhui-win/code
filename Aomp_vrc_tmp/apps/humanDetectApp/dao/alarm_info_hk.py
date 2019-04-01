# coding=utf-8

from datetime import datetime
from extensions import db
from common import AiMySQLDataError, HttpStatus, ai_print, constants, gen_uuid
import logging.config

logger = logging.getLogger()


class AlarmInfoHk(db.Model):
    __tablename__ = 'ALRM_INFO_HK'
    id = db.Column(db.String(36), default=gen_uuid, primary_key=True)
    ccbins_id = db.Column(db.String(9))
    eqmt_id = db.Column(db.String(20))
    orig_lgc_sn = db.Column(db.String(120))
    cct_rcrd_inf = db.Column(db.String(300))
    stdt_tm = db.Column(db.DateTime)
    bsn_cgycd = db.Column(db.String(2))
    vlt_err_alrm_inf = db.Column(db.String(120))
    uploadfiletrgtrfullnm = db.Column(db.String(120))
    last_udt_dt_tm = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    alarm_level = db.Column(db.String(120))


def add_record(alarm_info_hk_po):
    try:
        db.session.add(alarm_info_hk_po)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise AiMySQLDataError(HttpStatus.SERVER_ERROR, message='操作数据库失败')
