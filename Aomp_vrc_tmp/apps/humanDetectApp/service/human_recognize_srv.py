# coding=utf-8

import os
import numpy as np
import tensorflow as tf
from scipy import misc
from apps.humanDetectApp.models.facenet.align import detect_face
from apps.humanDetectApp.models.facenet import facenet
from common import (AiException, AiErrorCode, constants, HttpStatus)
import cv2 as cv
import logging.config
import math
from common import ai_print
from apps.humanDetectApp.human_detect_config import yaml_cfg
from apps.humanDetectApp.dao.read_face_from_db import read_from_db
import apps.humanDetectApp.dao.face_feture_info as face_feture_dao
from extensions import scheduler
logger = logging.getLogger()


class HumanRecognizeSrv:
    #初始化
    def __init__(self):
        # 扣人脸模型初始化
        self.minsize = yaml_cfg.get('facenet_min_size')  # minimum size of face
        # three steps's threshold
        self.threshold = list(map(float, yaml_cfg.get('facenet_threshold').split(',')))
        self.factor = float(yaml_cfg.get('facenet_factor'))  # scale factor
        self.margin = 44
        self.image_size = int(yaml_cfg.get('facenet_image_size'))
        self.graph_find = tf.Graph()
        self.facenet_confidence_level = float(yaml_cfg.get('facenet_confidence_level'))
        self.facenet_ingore_small = yaml_cfg.get('facenet_ingore_small')

        self.head_pitch_angle = 35  # 人员点头最大角度
        self.head_yaw_angle = 35  # 人员侧脸最大角度
        self.head_pitch_yaw_angle = 60  # 人员点后/侧脸角度和最大值
        self.face_color_percent = 0.6  # 符合人脸颜色的像素占整个人脸区域的比重最小值

        with self.graph_find.as_default():
            # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
            # self.sess_find = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            self.sess_find = tf.Session()
            with self.sess_find.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(self.sess_find, None)

        # 识别人脸模型初始化
        self.graph_recognize = tf.Graph()
        with self.graph_recognize.as_default():
            # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
            # self.sess_recognize = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            self.sess_recognize = tf.Session()
            with self.sess_recognize.as_default():
                # Load the model
                # facenet.load_model("20170512-110547")
                saver = tf.train.import_meta_graph("apps/humanDetectApp/models/facenet/20170512-110547/model-20170512-110547.meta")
                saver.restore(tf.get_default_session(), "apps/humanDetectApp/models/facenet/20170512-110547/model-20170512-110547.ckpt-250000")
                # saver = tf.train.import_meta_graph(
                #     "apps/humanDetectApp/models/facenet/20180402-114759/model-20180402-114759.meta")
                # saver.restore(tf.get_default_session(),
                #               "apps/humanDetectApp/models/facenet/20180402-114759/model-20180402-114759.ckpt-275")
                # Get input and output tensors
                self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
                self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
                self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        self.legal_ins_stuff = {}
        self.reg_ins_stuff()

    ########################以下从数据库或配置文件加载人脸、以及新增、修改、删除人脸的代码###############################
    def __reg_from_db(self, faces):
        # faces = read_from_db.db_face_infos
        ai_print(faces)
        tmp_legal_ins_stuff = {}
        for i in range(0, len(faces)):
            ccbinsId = faces[i].ccbins_id
            empeId = faces[i].ccb_empid
            usrNm = faces[i].usr_nm
            emb_str = faces[i].feture_info
            emb_list = emb_str.split(",")
            npArray_tmp = np.array(emb_list)
            ai_print(npArray_tmp)
            npArray = npArray_tmp.astype(np.float32)
            ai_print(npArray)
            tmp_ccbins = []
            for (key, value) in tmp_legal_ins_stuff.items():
                if key == ccbinsId:
                    tmp_ccbins = value
            if tmp_ccbins:
                tmp_ccbins.append({constants.cons_request_empe_id: empeId, constants.cons_request_usr_nm: usrNm,
                                   constants.cons_emb: npArray})
            else:
                tmp_legal_ins_stuff.update({ccbinsId: [
                    {constants.cons_request_empe_id: empeId, constants.cons_request_usr_nm: usrNm,
                     constants.cons_emb: npArray}]})
        self.legal_ins_stuff = tmp_legal_ins_stuff
        logger.info("从数据库注册人脸成功，人脸数: " + str(len(faces)))

    def __del_faces_by_ins(self,ccbins_id):
        if ccbins_id in self.legal_ins_stuff:
            self.legal_ins_stuff.pop(ccbins_id)

    def reload_faces_by_ins(self, ccbins_id):
        self.__del_faces_by_ins(ccbins_id)
        faces_of_inst = face_feture_dao.face_Feture_by_inst(ccbins_id)
        if faces_of_inst:
            self.__reg_from_db(faces_of_inst)
        logger.info("刷新人脸成功，机构号: " + ccbins_id+"，人脸数：" + str(len(faces_of_inst)))

    def __reg_from_file(self):
        stuff_image_dir = yaml_cfg.get('ccbins_stuff_imgs')
        list = os.listdir(stuff_image_dir)  # 列出文件夹下所有的目录与文件
        success = 0
        for i in range(0, len(list)):
            path = os.path.join(stuff_image_dir, list[i])
            if os.path.isfile(path):
                img = cv.imread(path)
                # cv.imwrite("src_file.jpg", img)
                img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                # cv.imwrite("src_file_rgb.jpg", img)
                embs = self.get_embedding(img)
                if len(embs) > 0:
                    success += 1
                    ccbinsId, empeId, usrNm = self.__getStuffInfoByPath(path)
                    tmp_ccbins = []
                    for (key, value) in self.legal_ins_stuff.items():
                        if key == ccbinsId:
                            tmp_ccbins = value
                    if tmp_ccbins:
                        tmp_ccbins.append({constants.cons_request_empe_id: empeId, constants.cons_request_usr_nm: usrNm,
                                           constants.cons_emb: embs[0]})
                    else:
                        self.legal_ins_stuff.update({ccbinsId: [
                            {constants.cons_request_empe_id: empeId, constants.cons_request_usr_nm: usrNm,
                             constants.cons_emb: embs[0]}]})
                else:
                    logger.error("图片中没有人脸, 路径:" + path)
        # print(self.legal_ins_stuff)
        logger.info("从配置文件注册人脸成功，人脸数: " + str(len(list)) + "，成功数量:"+str(success))

    def reg_ins_stuff(self):
        try:
            # 先从数据库装载人脸信息'
            self.__reg_from_db(read_from_db.db_face_infos)
            # 再从配置文件夹装载人脸信息
            self.__reg_from_file()
        except Exception:
            raise AiException(error_code=AiErrorCode.YCEA4021009)

    def __getStuffInfoByPath(self, filePath):
            file_name = os.path.basename(filePath)
            # 注册文件名形如111111111_12345678_吴昀蓁.jpg，
            # 前9位为机构编号，中间8位为员工编号，后面为姓名
            stuff_infos = file_name.split('_')
            return stuff_infos[0], stuff_infos[1], stuff_infos[2].split('.')[0]

    def __mod_ins_stuff(self, mnt_tp_cd, ccbins_id, empe_id, usr_nm, emb):
        ins_stuffs = self.legal_ins_stuff.get(ccbins_id)
        if ins_stuffs:
            if mnt_tp_cd == constants.cons_mnt_tp_cd_add:
                ins_stuffs.append({constants.cons_request_empe_id: empe_id,
                                   constants.cons_request_usr_nm: usr_nm, constants.cons_emb: emb})
            else:
                for i in range(len(ins_stuffs)):
                    if mnt_tp_cd == constants.cons_mnt_tp_cd_delete:
                        if ins_stuffs[i][constants.cons_request_empe_id] == empe_id:
                            ins_stuffs.pop(i)
                            break
                    else:
                        if ins_stuffs[i][constants.cons_request_empe_id] == empe_id:
                            ins_stuffs[i][constants.emb] = emb
                            break

    def mod_ins_stuff(self, empe_inf):
        mnt_tp_cd = empe_inf[constants.cons_request_mnt_tp_cd]
        tmp_emb = None
        if mnt_tp_cd == constants.cons_mnt_tp_cd_delete:
            self.__mod_ins_stuff(mnt_tp_cd, empe_inf[constants.cons_request_ccbins_id],
                                 empe_inf[constants.cons_request_empe_id], empe_inf[constants.cons_request_usr_nm],
                                 None)
        else:
            # 将图象由OpenCv的BGR转成RGB格式，wuyunzhen.zh, 20190309
            img = cv.cvtColor(empe_inf[constants.cons_request_img], cv.COLOR_BGR2RGB)
            tmp_embs = self.get_embedding(img)
            if len(tmp_embs) > 0:
                tmp_emb = tmp_embs[0]
                self.__mod_ins_stuff(mnt_tp_cd, empe_inf[constants.cons_request_ccbins_id],
                                     empe_inf[constants.cons_request_empe_id], empe_inf[constants.cons_request_usr_nm],
                                     tmp_emb)

                # 将图片保存到磁盘文件
                img_path = yaml_cfg.get('ccbins_stuff_pcs_imgs') + "/" + empe_inf[constants.cons_request_ccbins_id] + '_' + \
                           empe_inf[constants.cons_request_empe_id] + '_' + empe_inf[constants.cons_request_usr_nm] + ".jpg"
                cv.imwrite(img_path, empe_inf[constants.cons_request_img])
            else:
                raise AiException(HttpStatus.SERVER_ERROR,AiErrorCode.YCEA4021011)
        return tmp_emb

    # 定时任务装载人脸
    def schedule_task_reg_ins_stuff(self):
        try:
            with scheduler.app.app_context():
                faces_of_inst = face_feture_dao.face_Fetures()
                # 先从数据库装载人脸信息'
                self.__reg_from_db(faces_of_inst)
                # 再从配置文件夹装载人脸信息
                self.__reg_from_file()
        except Exception:
            raise AiException(error_code=AiErrorCode.YCEA4021009)

    # 重新计算人脸库特征向量
    def re_compute_featrue_from_db(self):
        try:
            faces_of_inst = face_feture_dao.face_Fetures()
            for i in range(0, len(faces_of_inst)):
                try:
                    id = faces_of_inst[i].id
                    uploadfiletrgtrfullnm = faces_of_inst[i].uploadfiletrgtrfullnm
                    img = cv.imread(uploadfiletrgtrfullnm)
                    # 将图象由OpenCv的BGR转成RGB格式，wuyunzhen.zh, 20190309
                    img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                    tmp_embs = self.get_embedding(img)
                    if len(tmp_embs) > 0:
                        logger.info("计算人脸特征:")
                        emb = tmp_embs[0].reshape(-1)
                        # 将ndArray转byte，再将byte转字符串
                        emb_list = emb.tolist()
                        data = ",".join(str(s) for s in emb_list)
                        face_feture_dao.update_fetures(id, data)
                    else:
                        logger.error("未找到人脸:"+uploadfiletrgtrfullnm)
                except Exception:
                    logger.error("重新计算人脸特征失败,id:" + faces_of_inst[i].id + ", path:" + faces_of_inst[i].uploadfiletrgtrfullnm)
        except Exception:
            raise AiException(error_code=AiErrorCode.YCEA4021009)

    ########################以上从数据库或配置文件加载人脸、以及新增、修改、删除人脸的代码###############################








    ########################以下是扣人脸的代码###############################
    def face_orientation(self, frame, landmarks):
        if len(landmarks) <10:
            return (0, 0), (0, 0), 0, 0, 0
        size = frame.shape  # (height, width, color_channel)

        model_points = np.array([
            (-165.0, 170.0, -115.0),  # Left eye left corner
            (165.0, 170.0, -115.0),  # Right eye right corne
            (0.0, 0.0, 0.0),  # Nose tip
            (-150.0, -150.0, -125.0),  # Left Mouth corner
            (150.0, -150.0, -125.0)  # Right mouth corner
        ])

        # Camera internals
        center = (size[1] / 2, size[0] / 2)
        focal_length = size[1]
        camera_matrix = np.array(
            [[focal_length, 0, center[0]],
             [0, focal_length, center[1]],
             [0, 0, 1]], dtype="double"
        )
        # 鼻尖起点
        p1 = (0, 0)
        dist_coeffs = np.zeros((4, 1))  # Assuming no lens distortion
        image_points = np.array([
            (landmarks[0], landmarks[1]),  # Left eye left corner
            (landmarks[2], landmarks[3]),  # Right eye right corne
            (landmarks[4], landmarks[5]),  # Nose tip
            (landmarks[6], landmarks[7]),  # Left Mouth corner
            (landmarks[8], landmarks[9])  # Right mouth corner
        ], dtype="double")
        # print(image_points)
        (success, rotation_vector, translation_vector) = cv.solvePnP(model_points, image_points, camera_matrix,
                                                                      dist_coeffs, flags=cv.SOLVEPNP_ITERATIVE)
        # 鼻尖起点
        p1 = (int(image_points[2][0]), int(image_points[2][1]))

        (nose_end_point2D, jacobian) = cv.projectPoints(np.array([(0.0, 0.0, 1000.0)]), rotation_vector,
                                                         translation_vector, camera_matrix, dist_coeffs)


        # 鼻尖末端顶点
        p2 = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))

        axis = np.float32([[500, 0, 0],
                           [0, 500, 0],
                           [0, 0, 500]])

        imgpts, jac = cv.projectPoints(axis, rotation_vector, translation_vector, camera_matrix, dist_coeffs)
        modelpts, jac2 = cv.projectPoints(model_points, rotation_vector, translation_vector, camera_matrix,
                                          dist_coeffs)

        rvec_matrix = cv.Rodrigues(rotation_vector)[0]

        proj_matrix = np.hstack((rvec_matrix, translation_vector))
        eulerAngles = cv.decomposeProjectionMatrix(proj_matrix)[6]

        pitch, yaw, roll = [math.radians(_) for _ in eulerAngles]

        pitch = math.degrees(math.asin(math.sin(pitch)))
        roll = -math.degrees(math.asin(math.sin(roll)))
        yaw = math.degrees(math.asin(math.sin(yaw)))

        return p1, p2,roll,pitch,yaw

    def drawLine(self, img, _bounding_boxes, _points, _directLines, effectFlag):
        dets = _bounding_boxes[:, 0:4]  # 去掉了最后一个元素？
        if len(_points) > 0:
            # points_transposes = list(map(list, zip(*_points)))
            # print(_points)
            font = cv.FONT_HERSHEY_SIMPLEX
            for i in range(0, len(_points)):
                det = dets[i]
                flag = effectFlag[i]
                # if not flag:
                #     continue
                cv.rectangle(img, (int(det[0]), int(det[1])), (int(det[2]), int(det[3])), (55, 255, 155), 5)
                txt = str(int(_directLines[i][2])) + "," + str(int(_directLines[i][3])) + "," + str(int(_directLines[i][4])) + "," + str(effectFlag[i])
                cv.putText(img, txt, (int(det[2]), int(det[3])+5), font, 0.8, (255, 255, 255), 2)
                point = _points[i]
                # print(point)
                cv.circle(img, (point[0], point[1]), 1, (0, 0, 255), 2)
                cv.circle(img, (point[2], point[3]), 1, (0, 0, 255), 2)
                cv.circle(img, (point[4], point[5]), 1, (0, 0, 255), 2)
                cv.circle(img, (point[6], point[7]), 1, (0, 0, 255), 2)
                cv.circle(img, (point[8], point[9]), 1, (0, 0, 255), 2)
                cv.line(img, _directLines[i][0], _directLines[i][1], (255, 255, 0), 2)
        cv.imshow('process', img)

    def get_effect_face(self, img, bounding_boxes, bounding_boxes_margin, points_transposes):
        # if len(landmarks) > 0:
        #     points_transposes = list(map(list, zip(*landmarks)))
        directLines = []
        effectFlag = []
        points = []
        frame = img
        effect_face_num = 0
        if len(bounding_boxes) == len(points_transposes):
            for i in range(0, len(bounding_boxes)):
                landmark = [points_transposes[i][0], points_transposes[i][5],
                         points_transposes[i][1], points_transposes[i][6],
                         points_transposes[i][2], points_transposes[i][7],
                         points_transposes[i][3], points_transposes[i][8],
                         points_transposes[i][4], points_transposes[i][9]]
                nose_p1, nose_p2, roll, pitch, yaw = self.face_orientation(frame, landmark)
                ai_print(roll, pitch, yaw)
                points.append(landmark)
                directLines.append([nose_p1,nose_p2,roll,pitch,yaw])
                if abs(pitch) > self.head_pitch_yaw_angle or abs(yaw) > self.head_yaw_angle or (abs(pitch) + abs(yaw)) > self.head_pitch_yaw_angle:
                    effectFlag.append(False)
                    effect_face_num += effect_face_num
                else:
                    effectFlag.append(True)
        # self.drawLine(img, bounding_boxes, points, directLines, effectFlag)
        return effect_face_num, bounding_boxes, points, directLines, effectFlag

    def cr_otsu(self, img):
        """YCrCb颜色空间的Cr分量+Otsu阈值分割"""
        ycrcb = cv.cvtColor(img, cv.COLOR_RGB2YCR_CB)

        (y, cr, cb) = cv.split(ycrcb)
        cr1 = cv.GaussianBlur(cr, (5, 5), 0)
        _, skin = cv.threshold(cr1, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

        [rows, cols] = skin.shape
        skin_pixel_count = 0
        for i in range(rows - 1):
            for j in range(cols - 1):
                if skin[i, j] == 255:
                    skin_pixel_count += 1
        logger.info("人脸颜色像素比:" + str(skin_pixel_count) + "/" + str(rows*cols) + "=" + str(skin_pixel_count/(rows*cols)))
        # cv.namedWindow("image raw", cv.WINDOW_NORMAL)
        # cv.imshow("image raw", img)
        # cv.namedWindow("image CR", cv.WINDOW_NORMAL)
        # cv.imshow("image CR", cr1)
        # cv.namedWindow("Skin Cr+OTSU", cv.WINDOW_NORMAL)
        # cv.imshow("Skin Cr+OTSU", skin)
        #
        # dst = cv.bitwise_and(img, img, mask=skin)
        # cv.namedWindow("seperate", cv.WINDOW_NORMAL)
        # cv.imshow("seperate", dst)
        # cv.waitKey(-1)

        return skin_pixel_count * 1.0 / (rows * cols)

    def get_face_by_color(self, img, bounding_boxes, points):
        img_size = np.asarray(img.shape)[0:2]
        face_boungding_boxes = np.empty(shape=[0, 5])
        face_points = []
        # print(bounding_boxes)
        # print(points)
        if len(bounding_boxes) > 0:
            for i in range(0, len(bounding_boxes)):
                bb = np.zeros(4, dtype=np.int32)
                bb[0] = np.maximum(bounding_boxes[i][0], 0)
                bb[1] = np.maximum(bounding_boxes[i][1], 0)
                bb[2] = np.minimum(bounding_boxes[i][2], img_size[1])
                bb[3] = np.minimum(bounding_boxes[i][3], img_size[0])
                cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
                # cv.imwrite(str(i) + ".jpg", cropped)
                percent = self.cr_otsu(cropped)
                if percent > self.face_color_percent:
                    tmp = bounding_boxes[i]
                    face_boungding_boxes = np.append(face_boungding_boxes, [[tmp[0],tmp[1],tmp[2],tmp[3],tmp[4]]], axis=0)
                    # face_boungding_boxes = np.append(face_boungding_boxes, [bounding_boxes[i]], axis = 0)
                    face_points.append(points[i])
        # print(face_boungding_boxes)
        return face_boungding_boxes, face_points

    def get_face(self, image_rgb):
        img_list = []
        img_size = np.asarray(image_rgb.shape)[0:2]
        tmp_bounding_boxes, tmp_points = detect_face.detect_face(image_rgb, self.minsize, self.pnet, self.rnet, self.onet,
                                                         self.threshold, self.factor)
        points_transposes = list(map(list, zip(*tmp_points)))
        bounding_boxes, points = self.get_face_by_color(image_rgb, tmp_bounding_boxes, points_transposes)
        if len(bounding_boxes) < 1:
            #image_paths.remove(image)
            logger.debug("图片中没有人脸")
            return []
        else:
            dets = bounding_boxes[:, 0:4]  # 去掉了最后一个元素？
            for i in range(0, len(dets)):
                det = dets[i]
                bb = np.zeros(4, dtype=np.int32)
                # np.maximum：(X, Y, out=None) ，X 与 Y 逐位比较取其大者；相当于矩阵个元素比较
                bb[0] = np.maximum(det[0] - self.margin / 2, 0)  # margin：人脸的宽和高？默认为44
                bb[1] = np.maximum(det[1] - self.margin / 2, 0)
                bb[2] = np.minimum(det[2] + self.margin / 2, img_size[1])
                bb[3] = np.minimum(det[3] + self.margin / 2, img_size[0])
                cropped = image_rgb[bb[1]:bb[3], bb[0]:bb[2], :]
                # height = cropped.shape[0]
                # width = cropped.shape[1]
                # if self.facenet_ingore_small and (height < self.minsize or width < self.minsize):
                #     logger.info("忽略人脸，像素长宽小于" + str(self.minsize)+"，当前长宽分别为:" + str(width) + "," + str(height))
                #     continue
                aligned = misc.imresize(cropped, (self.image_size, self.image_size), interp='bilinear')

                # cv.imwrite(str(i) + ".jpg", aligned)

                # prewhitened = aligned
                prewhitened = facenet.prewhiten(aligned)
                img_list.append(prewhitened)
                # cv.imwrite(str(i)+".jpg", prewhitened)
            if len(img_list) > 0:
                images = np.stack(img_list)
                return images
            else:
                return []


    def get_face_from_path(self,image_paths):
        tmp_image_paths = image_paths.copy()
        img_list = []
        for image in tmp_image_paths:
            img = misc.imread(os.path.expanduser(image), mode='RGB')
            img_size = np.asarray(img.shape)[0:2]
            bounding_boxes, _ = detect_face.detect_face(img, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
            # bounding_boxes, _ = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)

            if len(bounding_boxes) < 1:
                image_paths.remove(image)
                ai_print("can't detect face, remove ", image)
                continue
            det = np.squeeze(bounding_boxes[0, 0:4])  # 去掉了最后一个元素
            bb = np.zeros(4, dtype=np.int32)
            # np.maximum：(X, Y, out=None) ，X 与 Y 逐位比较取其大者；相当于矩阵个元素比较
            bb[0] = np.maximum(det[0] - self.margin / 2, 0)  # margin：人脸的宽和高？默认为44
            bb[1] = np.maximum(det[1] - self.margin / 2, 0)
            bb[2] = np.minimum(det[2] + self.margin / 2, img_size[1])
            bb[3] = np.minimum(det[3] + self.margin / 2, img_size[0])
            cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]

            # cropped = img
            aligned = misc.imresize(cropped, (self.image_size, self.image_size), interp='bilinear')
            prewhitened = facenet.prewhiten(aligned)
            img_list.append(prewhitened)
        images = np.stack(img_list)
        return images


    # 输入图象必须为RGB格式
    def get_embedding(self,image_rgb):
        images_find = self.get_face(image_rgb)
        if len(images_find) > 0:
            feed_dict = {self.images_placeholder: images_find, self.phase_train_placeholder: False}
            embs = self.sess_recognize.run(self.embeddings, feed_dict=feed_dict)
            return embs
        else:
            return []
    ########################以上是扣人脸的代码###############################



    # 计算非法人员入侵
    def get_invalid_face(self, image, ccbinsId):
        un_num = 0
        ins_stuffs = self.legal_ins_stuff.get(ccbinsId)
        # 将图象由OpenCv的BGR转成RGB格式，wuyunzhen.zh, 20190309
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        embs = self.get_embedding(image)

        #存储合法人员列表
        valid_stff_list = []
        for emb in embs:
            if ins_stuffs:
                dists = []
                min_dist = 9999.9
                valid_empe_id = None
                for ins_stuff in ins_stuffs:
                    tmp_dist = np.sqrt(np.sum(np.square(np.subtract(emb, ins_stuff.get(constants.cons_emb)))))
                    logger.info("置信度:"+str(tmp_dist))
                    if tmp_dist < min_dist:
                        min_dist = tmp_dist
                        valid_empe_id = ins_stuff.get(constants.cons_request_empe_id)
                if min_dist > self.facenet_confidence_level:
                    un_num = un_num + 1
                    logger.error("有非法人员")
                else:
                    # 有合法人员
                    valid_stff_list.append(valid_empe_id)
            else:
                un_num = un_num + 1
        logger.info("facenet识别的总人数为：%d, 合法人数：%d" % (len(embs), len(embs)-un_num))
        valid_stff_list = list(set(valid_stff_list))
        logger.info("合法人员ID：" + ",".join(str(s) for s in valid_stff_list))
        return len(embs), un_num,  valid_stff_list
