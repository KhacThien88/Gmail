from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
from flask_login import UserMixin


database=declarative_base()

class Users(database, UserMixin):
    __tablename__ = 'Users'

    UserID = Column("UserID", Integer, primary_key=True, autoincrement=True)
    UserNames = Column("UserNames", String, nullable=False)
    Passwords = Column("Passwords", String, nullable=False)
    MailServer = Column("MailServer", String, nullable=False)
    Smtp_port = Column("Smtp_port", Integer)
    Pop3_port = Column("Pop3_port", Integer)
    Autoload = Column("Autoload", Integer, default=10)

    def __init__(self, UserNames, Passwords, MailServer, Smtp_port, Pop3_port, Autoload):
        self.UserNames = UserNames
        self.Passwords = Passwords
        self.MailServer = MailServer
        self.Smtp_port = Smtp_port
        self.Pop3_port = Pop3_port
        self.Autoload = Autoload

class Folders(database, UserMixin):
    __tablename__ = 'Folders'
    
    FolderID = Column("FolderID", Integer, primary_key=True, autoincrement=True)
    FolderName = Column("FolderName", String, nullable=False)
    UserID = Column("UserID", Integer, ForeignKey('Users.UserID'))
    user = relationship('Users', backref='Folders')

    def __init__(self,FolderName,UserID):
        self.FolderName =FolderName
        self.UserID = UserID


class Emails(database, UserMixin):
    __tablename__ = 'Emails'

    EmailID = Column("EmailID", Integer, primary_key=True, autoincrement=True)
    Sender = Column("Sender", String, nullable=False)
    To_addr = Column("To_addr", String, nullable=False)
    Sub = Column("Sub", String, nullable=False)
    Cc = Column("Cc", String)
    Body = Column("Body", Text, nullable=False)
    FolderID = Column("FolderID", Integer, ForeignKey('Folders.FolderID'))
    IsCheck = Column("IsCheck", Boolean)
    HasFile = Column("HasFile", Boolean)
    folder = relationship('Folders',backref='Emails')

    def __init__(self,Sender, To_addr, Sub, Body, FolderID, IsCheck, Cc, HasFile):
        self.Sender = Sender
        self.To_addr = To_addr
        self.Sub = Sub
        self.Body = Body
        self.FolderID = FolderID
        self.IsCheck = IsCheck
        self.Cc=Cc
        self.HasFile = HasFile

class Files(database, UserMixin):
    __tablename__ = 'Files'

    FileID = Column("FileID", Integer, primary_key=True, autoincrement=True)
    FileNames = Column("FileNames", String, nullable=False)
    Base64Content = Column("Base64Content", String, nullable=False)
    EmailID = Column(Integer, ForeignKey('Emails.EmailID'))
    email=relationship('Emails',backref='Files')

    def __init__(self,EmailID,FileNames,Base64Content):
        self.EmailID = EmailID
        self.FileNames = FileNames
        self.Base64Content = Base64Content

def create_database():
    with open("config.json", 'r') as file:
        data = json.load(file)
    db_name = data.get('DB_NAME')
    engine = create_engine(f'sqlite:///{db_name}.db')
    database.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    session.commit()
create_database()
