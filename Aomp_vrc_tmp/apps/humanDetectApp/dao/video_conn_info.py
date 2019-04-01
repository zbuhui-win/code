# coding=utf-8

from datetime import datetime
from extensions import db
from common import AiMySQLDataError, HttpStatus, ai_print, constants, gen_uuid
import logging.config

logger = logging.getLogger()


class VideoConnInfo(db.Model):
    __tablename__ = 'VIDEO_CONN_INFO'
    id = db.Column(db.String(36), default=gen_uuid, primary_key=True)
    ccbins_id = db.Column(db.String(9))
    eqmt_id = db.Column(db.String(20))
    index_code = db.Column(db.String(120))
    cct_rcrd_inf = db.Column(db.String(300))
    status = db.Column(db.String(2))
    param1 = db.Column(db.String(120))
    param2 = db.Column(db.String(120))
    param3 = db.Column(db.String(120))
    param4 = db.Column(db.String(120))
    param5 = db.Column(db.String(120))
    param6 = db.Column(db.String(120))
    param7 = db.Column(db.String(120))
    param8 = db.Column(db.String(120))
    param9 = db.Column(db.String(120))
    param10 = db.Column(db.String(120))
    last_udt_dt_tm = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


def add_record(video_conn_info):
    try:
        db.session.add(video_conn_info)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise AiMySQLDataError(HttpStatus.SERVER_ERROR, message='操作数据库失败')
