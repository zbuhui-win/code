from extensions import db
from apps.humanDetectApp.dao.face_feture_info import FaceFetureInfo
from common import ai_print


class ReadFromDb(object):
    db_face_infos = None

    def read_db(self, app):
        with app.app_context():
            self.db_face_infos = db.session.query(FaceFetureInfo).filter_by(status='00').all()
            ai_print(self.db_face_infos)
            db.session.close()


read_from_db = ReadFromDb()


