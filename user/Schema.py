import datetime
from mongoengine import *
from bson.json_util import default
from flask_mongoengine import MongoEngine
import uuid
import mongoengine
from mongoengine.fields import BooleanField, DateTimeField, FileField, ReferenceField, StringField
# from mongoengine.fields import ReferenceField
db = MongoEngine()


class User(db.Document):

    name = db.StringField(required=True)
    email = db.EmailField(required=True)
    password = db.StringField(required=True)
    isTeacher = db.BooleanField(default=False)
    classroom_Joined = db.ObjectIdField(default=None)


class Classroom(db.Document):
    cid = db.StringField(primary_key=True)
    cname = db.StringField(required=True)
    student = db.ListField(db.DictField(), default=list)
    teacher = db.ListField(db.DictField(), default=list)


class Assignment(db.Document):
    cid = db.StringField(primary_key=True)
    title = db.StringField(required=True)
    desc = db.StringField(required=True)
    file = db.FileField()
    # filename = StringField()
    addDate = db.DateTimeField(default=datetime.datetime.now())
    dueDate = db.DateTimeField()
    isAttendance = db.BooleanField(default=False)
    isMissing = db.BooleanField(default=False)
    onClass = db.ReferenceField(Classroom)


class Submission(db.Document):
    isLate = db.BooleanField()
    subDate = db.DateTimeField(default=datetime.datetime.now())
    file = db.FileField()
    onAssign = db.ReferenceField(Assignment)
