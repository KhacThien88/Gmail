from flask import Blueprint, render_template, flash, request, jsonify,current_app
from flask_login import login_required, current_user
from flask.helpers import url_for
from werkzeug.utils import redirect,secure_filename
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session
from sendmail import MailSender,Message
from getmail import MailGetter
from models import *
import json
import os

views = Blueprint("views", __name__)
ALLOWED_EXTENSIONS = set(['txt','pdf','png','jpg','jpeg','gif'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

with open("config.json", 'r') as file:
    data = json.load(file)
DB_NAME = data.get('DB_NAME')

engine = create_engine(f'sqlite:///{DB_NAME}.db')
database.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session_maker = Session() 

@views.route("/home", methods=["GET", "POST"])
@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    username = session.get('username')
    password = session.get("password")

    if request.method == "GET" and 'username' not in session:
        return redirect("/signin")

    if request.method == "POST":
        To = request.form.get("to")
        Cc = request.form.get("cc")
        Bcc = request.form.get("bcc")

        if ',' in To:
            to = To.split(',')
            to = [t.strip() for t in to]
        elif To:
            to = [To]
        else: 
            to = None
        print(to)
        if ',' in Cc:
            cc = Cc.split(",")
            cc = [c.strip() for c in cc]
        elif Cc:
            cc = [Cc]
        else: 
            cc = None

        print(cc)

        if ',' in Bcc:
            bcc = Bcc.split(",")
            bcc = [b.strip() for b in bcc]
        elif Bcc:
            bcc = [Bcc]
        else: 
            bcc = None

        Subject = request.form.get("subject")
        Content = request.form.get("message")

        file = request.files['fileInput']
        filename = secure_filename(file.filename)
        file_paths = []
        print(file)
        if file and allowed_file(file.filename):
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],filename)
            file_paths.append(file_path)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],filename))


        message = Message(subject=Subject, body=Content, fromaddr=username, to=to, cc=cc, attachments=file_paths)

        Sender = MailSender(username, password)
        Sender.send_email(message, send_to=to, send_cc=cc, send_bcc=bcc)

    return render_template("home.html",user=username)

@views.route('/get-datas', methods=['GET'])
def get_datas():
    username = session.get('username')
    password = session.get("password")
    getter = MailGetter(username,password)
    getter.delete_and_save_database()
    folders =['Inbox', 'Important', 'Spam', 'Work', 'Project']
    datas = []
    for folder in folders:
        data = getter.makeDatas(folder)
        datas.extend(data)
    return jsonify(datas)

@views.route('/update-folder', methods=['POST'])
def update_datas():
    data = request.get_json()
    email_id = data.get('EmailID')
    new_folder = data.get('newFolder')
    username = session.get('username')
    print(username)
    user = session_maker.query(Users).filter_by(UserNames=username).first()
    fold = session_maker.query(Folders).filter_by(FolderName=new_folder,UserID=user.UserID).first()
    updateFolderID = session_maker.query(Emails).filter_by(EmailID=email_id).first()
    if updateFolderID:
        updateFolderID.FolderID = fold.FolderID
        session_maker.commit()
    return jsonify({})

@views.route('/update-isCheck', methods=['POST'])
def update_isCheck():
    data = request.get_json()
    email_id = data.get('EmailID')
    new_folder = data.get('isCheck')
    username = session.get('username')
    user = session_maker.query(Users).filter_by(UserNames=username).first()
    fold = session_maker.query(Folders).filter_by(FolderName=new_folder,UserID=user.UserID).first()
    email = session_maker.query(Emails).filter_by(EmailID=email_id).first()
    if email:
        email.IsCheck = True
        session_maker.commit()
    return jsonify({})
