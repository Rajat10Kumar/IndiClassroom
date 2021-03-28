from flask import Flask, render_template, session, redirect, jsonify, request, sessions, make_response
from functools import wraps
from passlib.hash import pbkdf2_sha256
# from flask_mongoengine import MongoEngine
from user.Schema import db
# import pymongo
from user.models import Register
from user.Schema import User, Classroom
app = Flask(__name__)
app.secret_key = 'test'
# client = pymongo.MongoClient('localhost',27017)
# db = client.user_login_system
app.config['MONGODB_SETTINGS'] = {
    'db': 'user_login_system',
    'host': 'localhost',
    'port': 27017
}
# db = MongoEngine()
db.init_app(app)


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
    return render_template('dashboard.html')


@app.route('/classroom/')
@is_admin
def classroom():
    return render_template('classroom.html')


@app.route('/classroom/create', methods=['POST'])
@is_admin
def create():
    data = request.form
    
    print(data["name"])
    return jsonify({"msg": "done"}), 200


if __name__ == "__main__":
    app.run(debug=True)
