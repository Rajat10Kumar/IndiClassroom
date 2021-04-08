import datetime
import os
from re import sub
import uuid
from gridfs import GridFS
from bson import encode
from flask import Flask, render_template, session, redirect, jsonify, request, sessions, make_response
from functools import wraps
from passlib.hash import pbkdf2_sha256
from werkzeug.utils import get_content_type, secure_filename
# from flask_mongoengine import MongoEngine
from user.Schema import db
# import pymongo
import codecs
import bson
import base64
from user.models import Register
from user.Schema import User, Classroom, Assignment, Submission
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = 'test'
# client = pymongo.MongoClient('localhost',27017)
# db = client.user_login_system
UPLOAD_FOLDER = 'D:\VS Code'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
ROOT = os.path.abspath(os.path.dirname(__file__))
APP_NAME = os.path.basename(ROOT)


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
    data = request.form
    print(data['isTeacher'])
    # user.save()
    emailexist = User.objects(email=data['email']).first()
    if data['password'] != data['confirm_password']:
        return jsonify({"error": "Password didn't match"}), 400
    if emailexist:
        return jsonify({"error": "Email Exists Already"}), 400
    else:
        print(data['isTeacher'])
        user = User(name=data['name'], email=data['email'],
                    password=pbkdf2_sha256.encrypt(data['password']), isTeacher=data['isTeacher'])
        user.save()
        session['logged_in'] = True
        session['user'] = data
        if data['isTeacher']:
            session['is_admin'] = True
        else:
            session['is_admin'] = False
        return jsonify(user), 200
    # return jsonify({"error": "Signup Failed"}), 400


@app.route('/user/login', methods=['POST'])
def login():
    data = request.form
    user = User.objects(email=data['email']).first()
    # print(pbkdf2_sha256.verify(data['password'], user.password), user.name,user.email,user.isTeacher)
    if user and pbkdf2_sha256.verify(data['password'], user.password):
        return start_session(user)

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
    return render_template('base.html')


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
    return jsonify({"msg": "done"}), 200


@app.route('/dashboard/join', methods=['POST'])
@login_required
def join():
    data = request.form
    id = data["code"]
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
    return jsonify({"msg": "done"}), 200


@app.route('/view/<string:id>', methods=['GET'])
def view_class(id):
    view_class = Classroom.objects(cid=id).first()
    asst = Assignment.objects(onClass=id)
    img = []
    for i in asst:
        photo = codecs.encode(i.file.read(), 'base64')
        img.append(photo.decode('utf-8'))
    return render_template('viewclass.html', data=view_class, assign=asst, image=img), 200
    # return jsonify(view_class), 200


@app.route('/enter/<string:id>', methods=['GET'])
def enter_class(id):
    view_class = Classroom.objects(cid=id).first()
    asst = Assignment.objects(onClass=id)
    img = []
    for i in asst:
        photo = codecs.encode(i.file.read(), 'base64')
        img.append(photo.decode('utf-8'))
    # print(type(asst[0].id))
    return render_template('enterclass.html', data=view_class, assign=asst, image=img), 200
    # return render_template('tabs.html'), 200
    # return jsonify(obj), 200


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
    return render_template('enterclass.html', data=view_class, assign=asst, image=img, subasst=subasst), 200
    # return jsonify(subasst), 200
    # return redirect('/enter/'+cid)


@app.route('/assignment/<string:id>', methods=['POST'])
def assign_assignment(id):
    data = request.form
    print(data)
    file = request.files['file']
    filename = secure_filename(file.filename)
    print(filename)
    # assign = Assignment()
    # # with open(UPLOAD_FOLDER, 'rb') as fd:
    # # assign.file.put(fd, content_type='image/jpeg')
    # assign.file.put(os.path.join(ROOT, filename), encoding="utf-8")

    # return jsonify(data)

    # if file and allowed_file(file.filename):
    #     filename = secure_filename(file.filename)
    #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    d = data['date']
    on_class = Classroom.objects(cid=id).first()
    # # jsonify(on_class)
    # # print(on_class)
    # # print(len(date))
    # # print(float(date))
    # # print(type(date))
    # # for i in len(date):
    # #     print(date[i])
    # # datetime()
    year = int(d[0]+d[1]+d[2]+d[3])
    month = int(d[6])
    day = int(d[8]+d[9])
    hour = int(d[11]+d[12])
    minute = int(d[14]+d[15])
    # # assign = Assignment(title=data['title'],desc=data['desc'], dueDate=datetime.strptime(d+":00.Z", "%Y-%m-%dT%H:%M:%S.Z"), onClass=on_class)
    assign = Assignment()
    # assign.filename = filename
    # assign.dueDate = datetime.strptime(d+":00.Z", "%Y-%m-%dT%H:%M:%S.Z")
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
    # return jsonify(assign), 200
    # pass


if __name__ == "__main__":
    app.run(debug=True)
