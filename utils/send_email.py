from email import encoders
from email.mime.base import MIMEBase
from email.utils import formataddr
import json
import os
from dotenv import load_dotenv
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()

sender_email =  os.environ.get("SENDER_EMAIL")
receiver_email = "example@example.com"
password = os.environ.get("SENDER_EMAIL_PASSWORD")
smtp_server = os.environ.get("SMTP_SERVER")
smtp_server_port = os.environ.get("SMTP_SERVER_PORT")


def send_email_with_or_without_attachment(body, subject, sender_email=sender_email, receiver_email=receiver_email, password=password, smtp_server=smtp_server, smtp_server_port=smtp_server_port, filename=None):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] =  formataddr(('PyCon Togo Team', sender_email))
    msg['To'] = receiver_email

    msg.attach(MIMEText(body, 'html'))

    # Attachment
    if filename:
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(filename)}')
            msg.attach(part)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, smtp_server_port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
