import datetime
import os
import time
import threading
import uuid
from flask import Flask, render_template, session, redirect, jsonify, request, sessions, make_response, Response
from functools import wraps
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import get_content_type, secure_filename
# from flask_mongoengine import MongoEngine
from user.Schema import db
import pymongo
import codecs
from user.Schema import User, Classroom, Assignment, Submission, Subject, Attendance
from bson.objectid import ObjectId
from camera import VideoCamera
from Encoder import Encoder
from sm import get_Score
encoder = Encoder()

app = Flask(__name__)
app.secret_key = 'test'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ROOT = os.path.abspath(os.path.dirname(__file__))
APP_NAME = os.path.basename(ROOT)
attendance_name = ""


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.config['MONGODB_SETTINGS'] = {
    'db': 'user_login_system',
    'host': 'localhost',
    'port': 27017
}
# db = MongoEngine()
db.init_app(app)


# fs = GridFS(db)


@app.route('/user/signup', methods=['POST'])
def RegisterUser():
    print("here")
    data = request.form
    # user.save()
    emailexist = User.objects(email=data['email']).first()
    if data['password'] != data['confirm_password']:
        return render_template("home.html", error_msg="Password didn't match")
    if emailexist:
        return render_template("home.html", error_msg="Email Exists Already")
    else:
        print(data)
        try:
            user = User(name=data['name'], email=data['email'],
                        password=pbkdf2_sha256.encrypt(data['password']), isTeacher=data['isTeacher'])
            user.save()
            session['logged_in'] = True
            session['user'] = data
            if data['isTeacher']:
                session['is_admin'] = True
                return redirect("/classroom/")
            else:
                session['is_admin'] = False
                return redirect("/dashboard/")
        except:
            user = User(name=data['name'], email=data['email'],
                        password=pbkdf2_sha256.encrypt(data['password']), isTeacher=False)
            user.save()
            user = User.objects(email=data['email']).first()
            start_session(user)
            return redirect("/dashboard/")

        return jsonify(user), 200
    # return jsonify({"error": "Signup Failed"}), 400


@app.route('/user/login', methods=['POST'])
def login():
    data = request.form
    user = User.objects(email=data['email']).first()
    # print(pbkdf2_sha256.verify(data['password'], user.password), user.name,user.email,user.isTeacher)
    if user and pbkdf2_sha256.verify(data['password'], user.password):
        start_session(user)
    else:
        return render_template('login.html', error_msg="Invalid Credentails")
    if user.isTeacher:
        return redirect("/classroom/")
    else:
        return redirect("/dashboard")

    return jsonify({"error": "Invalid Credentails"}), 401


def start_session(user):
    session['logged_in'] = True
    session['user'] = user
    # print(session['user']['name'])
    if user.isTeacher:
        session['is_admin'] = True
        # return redirect('/classroom/', user)
    else:
        session['is_admin'] = False
        # return redirect('/dashboard/', user)
    return jsonify(user), 200


def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'is_admin' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap


# from user import routes #should be here only


@app.route('/user/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/')
def home():
    return render_template('title.html')


@app.route('/loginform')
def loginForm():
    return render_template('login.html')


@app.route('/signupform')
def signupForm():
    return render_template('home.html')


@app.route('/dashboard/')
@login_required
def dashboard():
    # email = session['user']['email']
    # foo = Classroom.objects()
    # for i in foo['student']:
    t = []
    teacher = session['user']
    invalid = {'_id', 'password'}
    obj = {x: teacher[x] for x in teacher if x not in invalid}
    foo = Classroom.objects(student__contains=obj)
    junk = 0
    for i in foo:
        junk += 1
    return render_template('dashboard.html', classroom=foo, Length=junk)


@app.route('/classroom/')
@is_admin
def classroom():
    t = []
    teacher = session['user']
    invalid = {'_id', 'password'}
    obj = {x: teacher[x] for x in teacher if x not in invalid}
    foo = Classroom.objects(teacher__contains=obj)
    junk = 0
    for i in foo:
        junk += 1
    return render_template('classroom.html', classroom=foo, Length=junk)


@app.route('/classroom/create', methods=['POST'])
@is_admin
def create():
    data = request.form
    t = []
    teacher = session['user']
    invalid = {'_id', 'password'}

    t.append({x: teacher[x] for x in teacher if x not in invalid})

    c = Classroom(cid=uuid.uuid4().hex, cname=data['name'], teacher=t)
    c.save()
    print(data["name"])
    return redirect("/classroom")


@app.route('/dashboard/join', methods=['POST'])
@login_required
def join():
    data = request.form
    id = data["code"]
    id = encoder.base64decode(id)
    # Classroom.obj
    foo = Classroom.objects(cid=id)
    a = []
    for i in foo:
        a = i.student
    teacher = session['user']
    invalid = {'_id', 'password'}
    obj = {x: teacher[x] for x in teacher if x not in invalid}
    flag = 1
    for i in a:
        if i == obj:
            flag = 0
    if flag == 1:
        a.append(obj)
    foo = Classroom.objects(cid=id).update(student=a)
    return redirect("/dashboard")


@app.route('/mark_present/<string:id>/<string:aid>', methods=['GET'])
def mark_present(id, aid):
    user = User.objects(email=id).first()
    att = Attendance.objects(cid=aid).first()
    a = att['students_marked']
    junk = {}
    junk['name'] = user['name']
    junk['email'] = user['email']
    junk['isTeacher'] = user['isTeacher']
    a.append(junk)
    att.update(students_marked=a)
    return redirect("/attendance_view/"+aid)


@app.route('/attendance_view/<string:id>', methods=['GET'])
def view_attendance(id):
    att = Attendance.objects(cid=id)
    # print(att)
    s1 = []
    ismarked = []
    for i in att:
        # s1 = i.classroom.student
        s1 = i.classroom.student

    # s1 = att['classroom']['student']
    s2 = att[0]['students_marked']
    # for i in s1:
    #     ismarked.append(i in s2)
    junk = []
    for i in s1:
        obj = {}
        print(i)
        obj['name'] = i['name']
        obj['email'] = i['email']
        obj['isPresent'] = i in s2
        junk.append(obj)
    # print(s1)
    # print(s2)
    print(junk)
    return render_template('attendance.html', junk=junk, aid=id)


@app.route('/view/<string:id>', methods=['GET'])
def view_class(id):
    session['class'] = id
    _id = encoder.base64encode(id)
    view_class = Classroom.objects(cid=id).first()
    asst = Assignment.objects(onClass=id)
    sub = Subject.objects(classroom=id)
    att = Attendance.objects(classroom=id)
    img = []
    for i in asst:
        photo = codecs.encode(i.file.read(), 'base64')
        img.append(photo.decode('utf-8'))
    print(asst.to_json())
    return render_template('viewclass.html', data=view_class, assign=asst, image=img, subjects=sub, att=att, _id=_id), 200
    # return jsonify(view_class), 200


@app.route('/enter/<string:id>', methods=['GET'])
def enter_class(id):
    view_class = Classroom.objects(cid=id).first()
    asst = Assignment.objects(onClass=id)
    done = []
    unDone = []
    missing = []
    submission = []
    done_img = []
    unDone_img = []
    missing_img = []
    for i in asst:
        subm = Submission.objects(onAssign=i.cid)
        photo = codecs.encode(i.file.read(), 'base64')
        junk = (photo.decode('utf-8'))
        if subm:
            done.append(i)
            done_img.append(junk)
            for j in subm:
                photo = codecs.encode(j.file.read(), 'base64')
                submission.append(photo.decode('utf-8'))
        elif i.dueDate < datetime.datetime.now():
            missing_img.append(junk)
            missing.append(i)
        else:
            unDone_img.append(junk)
            unDone.append(i)
    # print(type(asst[0].id))
    att = Attendance.objects(classroom=id)
    ans = []
    teacher = session['user']
    invalid = {'_id', 'password'}
    junk = {x: teacher[x] for x in teacher if x not in invalid}
    for i in att:
        obj = {}
        obj['subject'] = i.subject.name
        obj['date'] = i.dueDate
        obj['isMissing'] = junk in i.students_marked
        obj['link'] = '/attendance/' + i.cid
        obj['teacher'] = i.teacher.name
        if i.dueDate < datetime.datetime.now() and junk not in i.students_marked:
            obj["isAbsent"] = True
        else:
            obj["isAbsent"] = False

        ans.append(obj)

    subm = Subject.objects(classroom=id)
    marked_percentage = []
    # print(junk)
    for i in subm:
        junk_ = {}
        junk_["name"] = i.name
        junk_["total"] = len(Attendance.objects(subject=i.cid))
        junk_["marked"] = len(Attendance.objects(
            subject=i.cid, students_marked__contains=junk))
        marked_percentage.append(junk_)

    return render_template('enterclass.html', data=view_class, done=done, unDone=unDone, missing=missing,
                           submission=submission, done_img=done_img, unDone_img=unDone_img,
                           missing_img=missing_img, attendance=ans, marked_percentage=marked_percentage), 200
    # return render_template('tabs.html'), 200
    # return jsonify(obj), 200


@app.route('/studentInfo/<string:id>', methods=['GET'])
def studentInfo(id):
    view_class = Classroom.objects(cid=id).first()
    asst = Assignment.objects(onClass=id)
    done = []
    unDone = []
    missing = []
    submission = []
    done_img = []
    unDone_img = []
    missing_img = []
    for i in asst:
        subm = Submission.objects(onAssign=i.cid)
        photo = codecs.encode(i.file.read(), 'base64')
        junk = (photo.decode('utf-8'))
        if subm:
            done.append(i)
            done_img.append(junk)
            for j in subm:
                photo = codecs.encode(j.file.read(), 'base64')
                submission.append(photo.decode('utf-8'))
        elif i.dueDate < datetime.datetime.now():
            missing_img.append(junk)
            missing.append(i)
        else:
            unDone_img.append(junk)
            unDone.append(i)
    # print(type(asst[0].id))
    att = Attendance.objects(classroom=id)
    ans = []
    teacher = session['user']
    invalid = {'_id', 'password'}
    junk = {x: teacher[x] for x in teacher if x not in invalid}
    for i in att:
        obj = {}
        obj['subject'] = i.subject.name
        obj['date'] = i.dueDate
        obj['isMissing'] = junk in i.students_marked
        obj['link'] = '/attendance/' + i.cid
        if i.dueDate < datetime.datetime.now() and junk not in i.students_marked:
            obj["isAbsent"] = True
        else:
            obj["isAbsent"] = False

        ans.append(obj)

    subm = Subject.objects(classroom=id)
    marked_percentage = []
    # print(junk)
    for i in subm:
        junk_ = {}
        junk_["name"] = i.name
        junk_["total"] = len(Attendance.objects(subject=i.cid))
        junk_["marked"] = len(Attendance.objects(
            subject=i.cid, students_marked__contains=junk))
        marked_percentage.append(junk_)

    return render_template('studentInfo.html', data=view_class, done=done, unDone=unDone, missing=missing,
                           submission=submission, done_img=done_img, unDone_img=unDone_img,
                           missing_img=missing_img, attendance=ans, marked_percentage=marked_percentage), 200


@app.route('/submit/<id>/<cid>', methods=['POST'])
def submit_assignment(id, cid):
    file = request.files['file']
    filename = secure_filename(file.filename)
    # print(request.form['aid'])
    asst = Assignment.objects(cid=id).first()
    # print(id, cid)

    subasst = Submission()
    dueDate = asst['dueDate']
    currDate = datetime.datetime.now()
    # # print(dueDate.date(), dueDate.time())
    # print(dueDate, currDate)
    # print(dueDate < currDate)
    if currDate > dueDate:
        subasst.isLate = True
        print("Late")
    else:
        subasst.isLate = False
        print("Not Late")
    subasst.file.put(file, content_type='image/jpeg')
    subasst.onAssign = asst
    subasst.save()
    view_class = Classroom.objects(cid=cid).first()
    asst = Assignment.objects(onClass=cid)
    img = []
    for i in asst:
        photo = codecs.encode(i.file.read(), 'base64')
        img.append(photo.decode('utf-8'))
    return redirect("/enter/"+cid)


@app.route('/assignment/<string:id>', methods=['POST'])
def assign_assignment(id):
    data = request.form
    print(data)
    file = request.files['file']
    filename = secure_filename(file.filename)
    print(filename)
    d = data['date']
    on_class = Classroom.objects(cid=id).first()
    year = int(d[0] + d[1] + d[2] + d[3])
    month = int(d[6])
    day = int(d[8] + d[9])
    hour = int(d[11] + d[12])
    minute = int(d[14] + d[15])
    assign = Assignment()
    assign.dueDate = datetime.datetime(year=year, month=month,
                                       day=day, hour=hour, minute=minute)
    assign.title = data['title']
    assign.desc = data['desc']
    assign.file.put(file, content_type='image/jpeg')
    assign.cid = uuid.uuid4().hex
    assign.onClass = on_class
    assign.save()
    asst = Assignment.objects(onClass=id)
    view_class = Classroom.objects(cid=id).first()
    print(asst)
    img = []
    for i in asst:
        photo = codecs.encode(i.file.read(), 'base64')
        img.append(photo.decode('utf-8'))
    return redirect('/view/' + id)


@app.route('/postSubject/<string:id>', methods=['POST'])
def postSubject(id):
    data = request.form
    on_class = Classroom.objects(cid=id).first()
    name = data["name"]
    sub = Subject()
    sub.cid = uuid.uuid4().hex
    sub.classroom = on_class
    sub.name = name
    sub.save()
    return redirect('/view/' + id)


@app.route('/postAttendance/<string:id>', methods=['POST'])
def postAttendance(id):
    data = request.form
    on_class = Classroom.objects(cid=id).first()
    subj = Subject.objects(cid=data["subject"]).first()
    att = Attendance()
    d = data['date']
    year = int(d[0] + d[1] + d[2] + d[3])
    month = int(d[6])
    day = int(d[8] + d[9])
    hour = int(d[11] + d[12])
    minute = int(d[14] + d[15])
    att.dueDate = datetime.datetime(
        year=year, month=month, day=day, hour=hour, minute=minute)
    att.cid = uuid.uuid4().hex
    att.classroom = on_class
    att.subject = subj
    att.teacher = User.objects(email=session["user"]['email']).first()
    att.save()
    return redirect('/classroom/')


@app.route('/attendance/<string:id>')
def index(id):
    return render_template('index.html', id=id)


@app.route('/markedPerson/<string:id>', methods=["POST"])
def marked_person(id):
    teacher = session['user']
    invalid = {'_id', 'password'}
    obj = {x: teacher[x] for x in teacher if x not in invalid}
    foo = Attendance.objects(cid=id)
    a = []
    for i in foo:
        a = i.students_marked

    flag = 1
    for i in a:
        if i == obj:
            flag = 0
    if flag == 1:
        a.append(obj)
    foo = Attendance.objects(cid=id).update(students_marked=a)
    return redirect("/dashboard")


def gen(camera):
    while True:
        frame, Names = camera.get_frame()
        global attendance_name
        if len(Names) == 20 and len(attendance_name) < 1:
            Max = 0
            MaxName = ""
            for i in Names:
                Count = 0
                for j in Names:
                    if i == j:
                        Count += 1
                if Count >= Max:
                    Max = Count
                    MaxName = i
            attendance_name = MaxName

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/getStudent/<string:id>')
def student(id):
    ret = []
    clss = Classroom.objects(cid=id)
    for i in clss:
        for j in i.student:
            uer = User.objects(email=j['email'])
            for k in uer:
                a = k.to_json()
                a['onClass'] = id
                print(a)
                ret.append(a)
    return render_template("studentList.html", slist=ret)


@app.route('/getStudentPost/<string:id>', methods=["POST"])
def getStudentPost(id):
    data = request.form
    pat = data['pat']
    ret = []
    print(pat)
    clss = Classroom.objects(cid=id)
    for i in clss:
        for j in i.student:
            uer = User.objects(email=j['email'])
            for k in uer:
                ret.append(k.to_json())
    ret = get_Score(pat, ret)
    print(ret)
    return render_template("studentList.html", slist=ret)


if __name__ == "__main__":
    app.run(debug=True)
