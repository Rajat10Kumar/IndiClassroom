from flask import Flask, render_template,session,redirect
from functools import wraps
import pymongo
app = Flask(__name__)
app.secret_key = 'test'
client = pymongo.MongoClient('localhost',27017)
db = client.user_login_system

def is_admin(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'is_admin' in session:
            return f(*args,**kwargs)
        else:
            return redirect('/')
    return wrap

def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            return redirect('/')
    return wrap

from user import routes #should be here only

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/loginform')
def loginForm():
    return render_template('login.html')

@app.route('/classroom/')
@is_admin
def classroom():
    return render_template('classroom.html')