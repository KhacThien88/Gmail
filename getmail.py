from socket import socket, AF_INET, SOCK_STREAM
import json
import re
import asyncio
from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
from email.parser import BytesParser
from email import policy

class MailGetter:
    def __init__(self, user_mail, user_password, pop3_server='127.0.0.1', pop3_port=276):
        self.user_mail = user_mail
        self.user_password = user_password
        self.pop3_server = pop3_server
        self.pop3_port = pop3_port

    def connect_server(self):
        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            clientSocket.connect((self.pop3_server, self.pop3_port))
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "+OK":
                print('ERROR connection')
            #else:
                #print("Message response:   " + recv)
        except ConnectionError:
            print("Mail error: Server unavailable or connection refused")
        return clientSocket

    def logging(self, clientSocket):
        clientSocket.sendall(f'USER {self.user_mail}\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "+OK":
            print('ERROR LOGGING USERNAME')
        #else:
            #print("Message response after send username:   " + recv)

        clientSocket.sendall(f'PASS {self.user_password}\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "+OK":
            print('ERROR LOGGING PASSWORD')
        #else:
            #print("Message response after send password: " + recv)

    def quit_server(self, clientSocket):
        clientSocket.sendall(f'QUIT\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "+OK":
            print('ERROR QUIT.')
        #else:
            #print("Message after QUIT:   " + recv)
        clientSocket.close()

    def receiveRes(self, clientSocket):
        clientSocket.settimeout(0.5)  
        recv = ''
        while True:
            try:
                data = clientSocket.recv(1024).decode()
                if not data:
                    break
                recv += data
            except :
                #print("Socket timeout occurred.")
                break
        return recv

    def mail_operation(self, clientSocket, operation, index=None):
        if operation == 'STAT':
            clientSocket.sendall(f'STAT\r\n'.encode())
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "+OK":
                print('ERROR OPERATION STAT')
            #else:
                #print("Message response after send STAT: " + recv)
        elif operation == 'LIST':
            clientSocket.sendall(f'LIST\r\n'.encode())
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "+OK":
                print('ERROR OPERATION LIST')
            #else:
                #print("Message response after send LIST: " + recv)
        elif operation == 'RETR':
            clientSocket.sendall(f'RETR {index}\r\n'.encode())  
            recv = self.receiveRes(clientSocket)
            if recv[:3] != "+OK":
                print('ERROR OPERATION RETR')
            #else:
                #print("Message response after send RETR: " + recv)
        elif operation == 'UIDL':
            clientSocket.sendall(f'UIDL\r\n'.encode())
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "+OK":
                   print('ERROR OPERATION UIDL')
            #else:
                #print("Message response after send UIDL: " + recv)
        elif operation == 'DELE':
            clientSocket.sendall(f'DELE {index}\r\n'.encode())
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "+OK":
                print('ERROR OPERATION DELE')
            #else:
                #print("Message response after send DELE:   " + recv)
        elif operation == 'RSET':
            clientSocket.sendall(f'RSET\r\n'.encode())  
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "+OK":
                print('ERROR OPERATION RSET')
            #else:
                #print("Message response after send RSET:   " + recv)
        return recv
    
    def extract_inf_thunderBird(self, retr_response):
        sender, subject, to, cc, content, filenames, base64_contents, hasFile = None, None, None, None, None, [], [], False

        lines = retr_response.split('\n')
        raw_content = '\n'.join(lines[1:-2])
        msg = BytesParser(policy=policy.default).parsebytes(raw_content.encode('utf-8'))

        subject = msg.get("Subject")
        sender = msg.get("From")
        to = msg.get("To")
        cc = msg.get("Cc")

        content = None
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or 'us-ascii' or 'utf-8'
                content = part.get_payload(decode=True).decode(charset)
                break

        boundary_match = re.search(r'boundary="([^"]+)"', retr_response)
        if boundary_match:
            boundary = boundary_match.group(1).strip()
        else:
            boundary = None

        if boundary:
            parts = re.split(boundary, retr_response)
            attachments = [part.strip() for part in parts if part.startswith('\r\nContent-Type:') 
                           and not part.startswith('\r\nContent-Type: text/plain; charset=UTF-8; format')]
            if(len(attachments) > 0):
                hasFile = True
            for attachment in attachments:
                filename_pattern = re.compile(r'Content-Disposition: attachment; filename="(.*?)"\r\nContent-Transfer-Encoding: base64\r\n\r\n(.*?)\r\n', re.DOTALL)
                filename_match = filename_pattern.search(attachment)
                if filename_match:
                    filename = filename_match.group(1).strip()
                else:
                    filename = None

                msg = attachment.split('\r\n\r\n')
                base64_content = '\r\n'.join(msg_element for i, msg_element in enumerate(msg) if i > 0 and i < len(msg)-1)
                filenames.append(filename)
                base64_contents.append(base64_content)
        return sender, subject, to, cc, content, filenames, base64_contents, hasFile, boundary

    def extract_inf_myMail(self, retr_response):
        sender, subject, to, cc, content, filenames, base64_contents, hasFile = None, None, None, None, None, [], [], False
        lines = retr_response.split('\n')
        raw_content = '\n'.join(lines[1:-2])
        msg = BytesParser(policy=policy.default).parsebytes(raw_content.encode('utf-8'))

        subject = msg.get("Subject")
        sender = msg.get("From")
        to = msg.get("To")
        cc = msg.get("Cc")

        content = None
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or 'us-ascii' or 'utf-8'
                content = part.get_payload(decode=True).decode(charset)
                break
        
        boundary_match = re.search(r'boundary="([^"]+)"', retr_response)
        if boundary_match:
            boundary = boundary_match.group(1).strip()
        else:
            boundary = None

        parts = re.split(boundary, retr_response)
        attachments = [part.strip() for part in parts if part.startswith("\r\nContent-Type: Application/Octet-stream")]
        if(len(attachments) > 0):
            hasFile = True

        for attachment in attachments:
            filename_pattern = re.compile(r'Content-Disposition: attachment; filename="(.+?)"', re.MULTILINE)
            filename_match = filename_pattern.search(attachment)
            if filename_match:
                filename = filename_match.group(1).strip()
            else:
                filename = None
            msg = attachment.split('\r\n\r\n')
            base64_content = '\r\n'.join(msg_element for i, msg_element in enumerate(msg) if i > 0 and i < len(msg)-1)
            filenames.append(filename)
            base64_contents.append(base64_content)
            
        return sender, subject, to, cc, content, filenames, base64_contents, hasFile, boundary

    def delete_and_save_database(self):
        clientSocket = self.connect_server()
        self.logging(clientSocket)
        stat = self.mail_operation(clientSocket, 'STAT').split(' ')

        for i in range(1,int(stat[1])+1):
            retr_response = self.mail_operation(clientSocket, 'RETR', i)

            sender, subject, to, cc, content, filenames, base64_contents, hasFile, boundary = self.extract_inf_thunderBird(retr_response)
            if boundary != None:
                if boundary.strip().startswith("="):
                    sender, subject, to, cc, content, filenames, base64_contents, hasFile, boundary = self.extract_inf_myMail(retr_response)

            self.save_email(sender, to, subject, content, cc, hasFile, filenames, base64_contents)
            self.mail_operation(clientSocket, 'DELE', i)
        self.quit_server(clientSocket)

    def delete(self):
        clientSocket = self.connect_server()
        self.logging(clientSocket)
        stat = self.mail_operation(clientSocket, 'STAT').split(' ')
        for i in range(1,int(stat[1])+1):
            self.mail_operation(clientSocket, 'DELE', i)
        self.quit_server(clientSocket)
    
    def save_email(self, sender, to_addr, subject, body, cc="", hasFile=False, fileNames= None, base64Datas=None):
        try:
            with open("config.json", 'r') as file:
                data = json.load(file)
            db_name = data.get('DB_NAME')
            engine = create_engine(f'sqlite:///{db_name}.db')
            Session = sessionmaker(bind=engine)
            session = Session()

            user_id = session.query(Users).filter_by(UserNames = self.user_mail).first()
            folder = self.folder_classification(sender, subject, body)
            folder_id = session.query(Folders).filter_by(FolderName = folder , UserID = user_id.UserID).first()

            newEmail = Emails(sender, to_addr, subject, body, folder_id.FolderID, False, cc, hasFile)
            session.add(newEmail)
            session.commit()
            
            if fileNames and base64Datas:
                for fileName, base64Data in zip(fileNames, base64Datas):
                    newFile = Files(newEmail.EmailID, fileName, base64Data)
                    session.add(newFile)
                session.commit()
        except Exception as e:
            print(f"Error storing email data into the database: {e}")
            session.rollback()
    
    def move_mail(self, emailID, to_folder):
        with open("config.json", 'r') as file:
            data = json.load(file)
            db_name = data.get('DB_NAME')
            engine = create_engine(f'sqlite:///{db_name}.db')
            Session = sessionmaker(bind=engine)
            session = Session()

        user = session.query(Users).filter_by(UserNames=self.user_mail).first()

        fold = session.query(Folders).filter_by(FolderName=to_folder,UserID=user.UserID).first()
        updateFolderID = session.query(Emails).filter_by(EmailID=emailID).first()
        if updateFolderID:
            updateFolderID.FolderID = fold.FolderID
            session.commit()


    def folder_classification(self, sender, subject, body):
        try:
            with open("config.json", 'r') as file:
                data = json.load(file)
            filters = data.get('filters')

            for filter_config in filters:
                filter_type = filter_config.get('type')
                filter_values = filter_config.get('values', [])

                if filter_type == 'Project' and sender in filter_values:
                    return 'Project'
                elif filter_type == 'Important' and any(value in subject for value in filter_values):
                    return 'Important'
                elif filter_type == 'Work' and any(value in body for value in filter_values):
                    return 'Work'
                elif filter_type == 'Spam' and (any(value in body for value in filter_values) or any(value in subject for value in filter_values)):
                    return 'Spam'
            return 'Inbox'
        except Exception as e:
            print(f"Error: {e}")
            return 'Inbox'
        
    def makeDatas(self,folderName):
            with open("config.json", 'r') as file:
                data = json.load(file)
            db_name = data.get('DB_NAME')
            engine = create_engine(f'sqlite:///{db_name}.db')
            Session = sessionmaker(bind=engine)
            session = Session()

            user = session.query(Users).filter_by(UserNames=self.user_mail).first()
            fold = session.query(Folders).filter_by(FolderName=folderName,UserID=user.UserID).first()
            datas = session.query(Emails).filter_by(FolderID=fold.FolderID).all()

            dataSend = []
            if len(datas) > 0:
                for data in datas:
                    emailID = data.EmailID
                    sender = self.user_mail
                    to = data.To_addr
                    cc = data.Cc
                    subject = data.Sub
                    content = data.Body
                    isCheck = data.IsCheck
                    hasFile = data.HasFile

                    file_names = []
                    base64_content = []
                    if(hasFile != None):
                        files = session.query(Files).filter_by(EmailID=emailID).all()
                        for file in files:
                            file_names.append(file.FileNames)
                            base64_content.append(file.Base64Content)
                        
                    dataSend.append({
                        "EmailID": emailID,
                        "forder": folderName,
                        "sender": sender,
                        "to": to,
                        "cc": cc,
                        "subject": subject ,
                        "content": content,
                        "attachment": file_names,
                        "isCheck" : isCheck ,
                        "base64content": base64_content,
                    })
            return dataSend
    
    async def delete_and_save_database_async(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.delete_and_save_database)

mail_getter = MailGetter("abc@gmail.com", '275276')
mail_getter.delete_and_save_database()
