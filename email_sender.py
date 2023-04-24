# -*- coding: utf-8 -*-
"""
    Functions to send notifications by email
"""

# Impedindo a geração do __pycache__
import sys
sys.dont_write_bytecode = True

# Common Imports
import os
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl


def send_email(
        receivers_email: list[str], 
        subject: str, body_message: str, 
        attachment_paths: list[str] = [],
        host: str = 'smtp.gmail.com', port: int = 587, 
        sender_email: str =  "vpzleiloes@gmail.com",
        password: str = None
        ):

    # If no password is provide, reads the password from environment variable.
    if password is None:
        password = os.environ['auction_email']

    # Creating object MIMEMultipart
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receivers_email[0]
    message["Subject"] = subject
    message["Cc"] = ";".join(receivers_email[1:]) 

    # Building email message with MIME object. 
    message.attach(MIMEText(body_message, "plain"))

    # If any files needs to be attached.
    for file_path in attachment_paths:
        # Open file as binary.
        with open(file_path, "rb") as attachment:
            # Adding file with application/octet-stream.
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # File encoding ASCII to send.
        encoders.encode_base64(part)

        # Adding header as pair key/value for attachment part.
        filename = re.sub('.*/','', file_path)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Adding attachment to message.
        message.attach(part)
    
    # Converting message to str.
    text = message.as_string()

    context = ssl.create_default_context()

    # Sending email
    with smtplib.SMTP(host = host, port= port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, receivers_email, text)