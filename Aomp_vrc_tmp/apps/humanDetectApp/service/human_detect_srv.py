# coding=utf-8

import logging.config
import common.constants as constants
from apps.humanDetectApp.human_detect_config import yaml_cfg
import time
import os
import cv2 as cv
import apps.humanDetectApp.dao.oprt_rcd_info as oprt_rcd_dao
from common import ai_print
logger = logging.getLogger()


class HumanDetectSrv(object):
    def __init__(self, humanCountSrv, humanRecognizeSrv):
        self.humanCountSrv = humanCountSrv
        self.humanRecognizeSrv = humanRecognizeSrv


    def humanDetect(self, req_data, cv_image_list, path_flag):
        results = []
        write_dbs = []
        cur_date = time.strftime('%Y%m%d', time.localtime(time.time()))
        ccbins_id = req_data.get(constants.cons_request_ccbins_id)
        sys_evt_trace_id = req_data.get(constants.cons_request_trace_id)
        folder_path = yaml_cfg.get('illegal_image_path') + "/" + cur_date +'/'+ ccbins_id
        save_all_file = yaml_cfg.get('save_all_file')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_path = os.path.abspath(folder_path)
        for i in range(0, len(cv_image_list)):
            face_count = 0
            #人数、非法人数为-1，表示该项无须校验
            human_count = -1
            un_num = -1
            valid_stff_list = []
            for type in req_data.get(constants.cons_request_model_type):
                if type == constants.cons_mdtp_human_detect:
                    # 人数检测
                    human_count = self.humanCountSrv.humanCount(cv_image_list[i])
                elif type == constants.cons_mdtp_human_recg:
                    # 非法入侵
                    face_count, un_num, valid_stff_list = self.humanRecognizeSrv.get_invalid_face(cv_image_list[i], ccbins_id)
            results.append([human_count, face_count, un_num, valid_stff_list])
            detect_alarm_flag, recognize_alarm_flag = self.__computeAlarm(human_count, un_num)
            img_path = (req_data.get(constants.cons_request_paths)[i] if path_flag else (
                        folder_path + "/" + sys_evt_trace_id + "_" + str(i) + ".jpg"))
            if not path_flag:
                if detect_alarm_flag or recognize_alarm_flag or save_all_file:
                    # 若不是通过交易带附件传图片且初步认为有告警产生，则保存图片
                    cv.imwrite(img_path, cv_image_list[i])

            # 将结果写数据库
            write_dbs.append([human_count, un_num, valid_stff_list, img_path, detect_alarm_flag, recognize_alarm_flag])
        oprt_rcd_dao.add_records(write_dbs, req_data)
        return results

    def __computeAlarm(self, human_count, un_num):
        legal_stuff_num = yaml_cfg.get('legal_stuff_num')
        return (human_count != -1 and human_count != 0 and human_count < legal_stuff_num), un_num > 0
