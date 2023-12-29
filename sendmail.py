from socket import socket, AF_INET, SOCK_STREAM
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class Message:
    def __init__(self, subject=None, to=None, body=None, fromaddr=None, cc=None, attachments=None):
        self.subject = subject
        self.body = body
        self.attachments = attachments 
        self.to = to 
        self.fromaddr = fromaddr
        self.cc = cc

    def as_string(self):
        msg = MIMEMultipart()
        msg['From'] = self.fromaddr
        msg['Subject'] = self.subject
        if self.cc :
            msg["Cc"] = ", ".join(self.cc)
        if self.to:
            msg['To'] = ", ".join(self.to)

        msg.attach(MIMEText(f'{self.body}'))

        if self.attachments:
            for attachment in self.attachments:
                part = MIMEBase('Application', 'Octet-stream')
                part.set_payload(open(attachment, 'rb').read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment)}"')
                msg.attach(part)
        #print(msg.get_content_maintype())
        return msg.as_string()

class MailSender:
    def __init__(self ,user_mail , password, smtp_server='127.0.0.1', smtp_port=275):
        self.user_mail = user_mail
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, message, send_to=None, send_cc=None, send_bcc=None):
        dest_to_addrs = []
        if send_cc:
            dest_to_addrs.extend(send_cc)
        if send_bcc:
            dest_to_addrs.extend(send_bcc)
        if send_to:
            dest_to_addrs.extend(send_to)

        clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            clientSocket.connect((self.smtp_server, self.smtp_port))
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "220":
                print('220 reply not received from server.')
            #else:
                #print("Message after connection request:   " + recv)
        except:
            print("mail error", "Server unavailable or connection refused")

        clientSocket.sendall(f'EHLO {self.smtp_server}\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "250":
            print('250 reply not received from server.')
        #else:
            #print("Message after EHLO :   " + recv)

        clientSocket.sendall(f'MAIL FROM: <{self.user_mail}>\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "250":
            print('220 reply not received from server.')
        #else:
            #print("Message after MAIL FROM:   " + recv)

        for to_addr in dest_to_addrs:
            clientSocket.sendall(f'RCPT TO: <{to_addr}>\r\n'.encode())
            recv = clientSocket.recv(1024).decode()
            if recv[:3] != "250":
                print('250 reply not received from server.')
            #else: 
                #print("Message after RCPT:   " + recv)

        clientSocket.sendall(f'DATA\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "354":
            print('354 reply not received from server.')
        #else: 
            #print("Message after DATA:   " + recv)

        clientSocket.sendall(message.as_string().encode())

        clientSocket.sendall(f'.\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "250":
            print('250 reply not received from server.')
        #else: 
            #print("Message after request'.':   " + recv)

        clientSocket.sendall(f'QUIT\r\n'.encode())
        recv = clientSocket.recv(1024).decode()
        if recv[:3] != "221":
            print('221 reply not received from server.')
        #else: 
            #print("Message after QUIT:   " + recv)
        clientSocket.close()

# mail_sender = MailSender('e@gmail.com', '123456')
# message = Message('Test Subject', body='test mail', fromaddr='lephucthuan8@gmail.com', to=['e@gmail.com'],cc=["hi.com","ttt.com","hihi.com" ], attachments=['./static/img/login.jpg'] )
# mail_sender.send_email(message,
#                     send_to=['e@gmail.com'],
#                     send_bcc=["hi.com","ttt.com","hihi.com" ],
#                         )