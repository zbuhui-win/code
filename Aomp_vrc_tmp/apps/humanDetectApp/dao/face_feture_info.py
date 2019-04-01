# coding=utf-8

from extensions import db
from common import gen_uuid
from datetime import datetime
from common import AiMySQLDataError,HttpStatus


class FaceFetureInfo(db.Model):
    __tablename__ = 'FACE_FETURE_INFO'
    id = db.Column(db.String(36), default=gen_uuid, primary_key=True)
    ccbins_id = db.Column(db.String(9))
    ccb_empid = db.Column(db.String(20))
    usr_nm = db.Column(db.String(20))
    feture_info = db.Column(db.String(3000))
    status = db.Column(db.String(2))
    uploadfiletrgtrfullnm = db.Column(db.String(500))
    last_udt_dt_tm = db.Column(db.DateTime, default=datetime.now)


def face_Feture_by_inst(ccbins_id):
    '''
    查询机构下所有人脸信息
    '''
    faces_of_inst = FaceFetureInfo.query.filter_by(ccbins_id=ccbins_id).filter_by(status='00').all()
    return faces_of_inst

def face_Fetures():
    '''
    查询机构下所有人脸信息
    '''
    faces_of_inst = FaceFetureInfo.query.filter_by(status='00').all()
    return faces_of_inst


def update_fetures(id, feture):
    '''
    查询机构下所有人脸信息
    '''
    face_feture = FaceFetureInfo.query.filter_by(id=id).first()
    face_feture.feture_info = feture
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise AiMySQLDataError(HttpStatus.SERVER_ERROR, message='操作数据库失败')
