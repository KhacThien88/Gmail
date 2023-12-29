from flask import session
from flask import Blueprint, render_template, request, flash, session
from flask.helpers import url_for
from werkzeug.utils import redirect
from models import *
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_bcrypt import Bcrypt

user = Blueprint("user", __name__)
bcrypt = Bcrypt()

with open("config.json", 'r') as file:
    data = json.load(file)
DB_NAME = data.get('DB_NAME')

engine = create_engine(f'sqlite:///{DB_NAME}.db')
database.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session_maker = Session() 

@user.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = session_maker.query(Users).filter_by(UserNames=email).first()
        if user:
            if user.Passwords == password:
                session['username'] = email
                session['password'] = password
                return redirect(url_for("views.home"))
            else:
                return render_template("signin.html", error_password='incorrect password!')
        return render_template("signin.html", error_username='incorrect username!')
    return render_template("signin.html")

@user.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        print(password)
        print(confirm_password)
        user = session_maker.query(Users).filter_by(UserNames=email).first()
        if user:
            render_template('signup.html', error_username="This username is existed.")
        elif password != confirm_password:
            render_template('signup.html', error_password="Password doesn't match.")
        else:
            new_user = Users(email, password, data.get('MailServer'),data.get('SMTP'), data.get('POP3'), data.get('Autoload'))
            session_maker.add(new_user)
            session_maker.commit()

            folders = ['Inbox', 'Project', 'Important', 'Work', 'Spam']
            for folder in folders:
                new_folder = Folders(folder,new_user.UserID)
                session_maker.add(new_folder)
                session_maker.commit()
            return redirect(url_for("user.signin"))
    return render_template('signup.html')


@user.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("user.signin"))

