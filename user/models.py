from flask import Flask, jsonify, request, session, redirect
from passlib.hash import pbkdf2_sha256
from user.Schema import User
# from app import db
# import uuid


class Register:
    def start_session(self, data):
        # del user['password']
        # del user['confirm_password']
        # print(user)
        # session['logged_in'] = True
        # # session['is_admin'] = False
        # if data["isTeacher"]:
        #     session["is_admin"] = True
        #     # print(session['is_admin'])
        # else:
        #     session["is_admin"] = False
        session['user'] = data
        # return jsonify(data), 200

    # def signup(self):
    #     data = request.form.get
    #     # print(data['name'])
    #     user = User(name=request.form.get('name'), email=request.form.get('email'), password=request.form.get(
    #         'password'), confirm_password=request.form.get('confirm_password'))
    #     return jsonify({"msg": "Done"})

    #     user = {
    #         "_id": uuid.uuid4().hex,
    #         "name": request.form.get('name'),
    #         "email": request.form.get('email'),
    #         "password": request.form.get('password'),
    #         "confirm_password": request.form.get('confirm_password'),
    #         "user_type": request.form.get('user_type')
    #     }
    #     # print(user["user_type"])
    #     if user['password'] != user['confirm_password']:
    #         return jsonify({"error": "Password didn't match"}), 400
    #     else:
    #         user['password'] = pbkdf2_sha256.encrypt(user['password'])
    #     if db.users.find_one({"email": user["email"]}):
    #         return jsonify({"error": "Email Exists Already"}), 400
    #     if db.users.insert_one(user):
    #         return self.start_session(user)
    #         # return jsonify(user), 200
    #     return jsonify({"error": "Signup Failed"}), 400

    # def logout(self):
    #     session.clear()
    #     return redirect('/')

    # def login(self):

    #     user = db.users.find_one({"email": request.form.get('email')})
    #     # print("hello")
    #     print(user)
    #     # print(user['email'], user['password'])
    #     if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
    #         return self.start_session(user)

    #     return jsonify({"error": "Invalid Credentails"}), 401
