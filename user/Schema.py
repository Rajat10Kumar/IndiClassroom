from bson.json_util import default
from flask_mongoengine import MongoEngine
import uuid
import mongoengine
db = MongoEngine()


class Classroom(db.Document):
    cid = db.IntField(uuid.uuid4().hex, primary_key=True)
    cname = db.StringField(required=True)
    student = db.ListField(mongoengine.ObjectIdField(), default=list)
    teacher = db.ListField(mongoengine.ObjectIdField(), default=list)


class User(db.Document):
    # sid = db.IntField(uuid.uuid4().hex)
    name = db.StringField(required=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    # confirm_password = db.IntField(required=True)
    isTeacher = db.BooleanField(default=False)
    classroom_Joined = db.ObjectIdField(db_field=None, default=None)
