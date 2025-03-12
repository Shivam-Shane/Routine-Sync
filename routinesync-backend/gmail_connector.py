import socket
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from logger import logger

class MailSender():
    def __init__(self):
        load_dotenv()
        self.SENDER_NAME_VALUE = os.getenv('SENDER_NAME')
        self.SENDER_EMAIL = os.getenv('SMTP_USERNAME')
        self.server_connection = None
        self.connect_to_smtp_server()

    def connect_to_smtp_server(self):
        try:
            self.server_connection = smtplib.SMTP(os.getenv("SMTP_SERVER"), os.getenv("SMTP_PORT"))
            self.server_connection.starttls()
            self.server_connection.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            logger.info("successfully authenicated with SMTP server")
        except (socket.gaierror, socket.timeout) as net_err:
            logger.error(f"Network issue while connecting to SMTP server: " + str(net_err))
            raise RuntimeError("Network issue while connecting to SMTP server: " + str(net_err))
        except ssl.SSLError as ssl_err:
            logger.info(f"SSL error while connecting to SMTP server: " + str(ssl_err))
            raise RuntimeError("SSL error while connecting to SMTP server: " + str(ssl_err))
        except smtplib.SMTPException as smtp_err:
            logger.info(f"SMTP error: " + str(smtp_err))
            raise RuntimeError("SMTP error: " + str(smtp_err))

    def sender(self,useremail,subject,body):
        try:
            msg = MIMEMultipart()
            msg['From'] = f'{self.SENDER_NAME_VALUE} <{self.SENDER_EMAIL}>'
            msg['To'] = useremail
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))  
            # Send the email
            self.server_connection.sendmail(self.SENDER_EMAIL, useremail, msg.as_string())
            return True
            
        except smtplib.SMTPException as e:
            # Reconnect if not connected
            logger.info("Unexpected error ouccured")
            self.connect_to_smtp_server()

