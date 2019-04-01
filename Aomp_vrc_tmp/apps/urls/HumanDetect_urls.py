# coding=utf-8

# import apps.humanDetectApp.controller.human_detect_ctrl as detect_ctr
# import apps.humanDetectApp.controller.stuff_reg_ctrl as stf_reg_ctr
import apps.humanDetectApp.controller.hk_alarm_ctrl as hk_alarm_ctr
import apps.humanDetectApp.controller.video_conn_info_ctrl as video_conn_ctrl
urls = [
    # '/detect/human', detect_ctr.HumanDetectCtrl,
    # '/detect/reg', stf_reg_ctr.StuffRegCtrl,
    # '/face/feture', stf_reg_ctr.FaceFetureCtrl,
    '/hk/alarm', hk_alarm_ctr.HkAlarmCtrl,
    '/video/conn', video_conn_ctrl.VideoConnInfoCtrl
]
