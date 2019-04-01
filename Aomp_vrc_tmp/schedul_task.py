# coding=utf-8
import logging.config
from apps.humanDetectApp.singleton import humanRecognizeSrv
from flask import current_app
logger = logging.getLogger()


def reload_face_from_db():
    # from apps.humanDetectApp.dao.read_face_from_db import read_from_db
    # read_from_db.read_db(current_app)
    # humanRecognizeSrv.reg_ins_stuff()
    humanRecognizeSrv.schedule_task_reg_ins_stuff()
    logger.info('定时任务数据库装载完成')

