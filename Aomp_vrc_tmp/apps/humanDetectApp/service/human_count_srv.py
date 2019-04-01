# coding=utf-8

import apps.humanDetectApp.models.pose_estimation.src.networks as networks
from apps.humanDetectApp.models.pose_estimation.src.estimator import TfPoseEstimator
from networks.yolo.yolo3_predict import YOLO
from PIL import Image
from common import addlog,ai_print
import tensorflow as tf
import logging.config
from keras import backend as K
from apps.humanDetectApp.human_detect_config import yaml_cfg
logger = logging.getLogger()
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = float(yaml_cfg.get('per_process_gpu_memory_fraction'))
session = tf.Session(config=config)
K.set_session(session)


class HumanCountSrv(object):
    def __init__(self):
        self.yolo_anchors_path = yaml_cfg.get('yolo_anchors_path')
        self.yolo_model_path = yaml_cfg.get('yolo_model_path')
        self.yolo_classes_path = yaml_cfg.get('yolo_classes_path')
        self.usr_model_type = yaml_cfg.get('usr_model_type')
        if self.usr_model_type == 'yolo':
            logger.info("use yolo model in human detecting")
            self.yolo = YOLO(self.yolo_anchors_path, self.yolo_model_path, self.yolo_classes_path)
        else:
            logger.info("use pose model in human detecting")
            w, h = networks.model_wh(yaml_cfg.get('pose_image_size'))
            self.poseEstimator = TfPoseEstimator(networks.get_graph_path('cmu'), target_size=(w, h))

    @addlog
    def humanCount(self, img):
        if self.usr_model_type == 'yolo':
            im = Image.fromarray(img)
            result = self.yolo.predict(im)
            human_num = 0
            if result:
                for i in range(len(result)):
                    if result[i][0] == 'person':
                        ### print('人数置信度:%f' % (result[i][1]))
                        human_num += 1
            logger.info("yolo人数为:"+str(human_num))
            return human_num
        else:
            humans = self.poseEstimator.inference(img)
            logger.info("open pose人数为:" + str(len(humans)))
            return len(humans)

