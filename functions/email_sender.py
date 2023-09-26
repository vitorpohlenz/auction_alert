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
import pandas as pd

def send_action_notification(
        data_df: pd.DataFrame,
        output_dir: str,
        user: str,
        filter_id: int,
        receiver_email: str,
        state: str = None,
        city: str = None,
        category: str = None
        ) -> None:
    """
    Function to prepare and send the data by email.

    Parameters
    ----------
    data_df : pd.DataFrame
        Data frame with auctions data of desired filter.
    output_dir : str
        Directory to save the data as attachment of email.
    user : str
        The user that wants to receive the email with the filtered data.
    filter_id : int
        FilterId of this data filtered.
    receiver_email : str
        Email of the user to receive the data by email.
    state : str, optional
        State of the filter, by default None
    city : str, optional
        City of the filter, by default None
    category : str, optional
        Category of the filter, by default None
    """

    # Creating output folder to save the file attachments if it doesn't exists.
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Building the email subject with not null information.
    message_subject = f"Auction notification for {user}"
    for s in (state, city, category):
        if not pd.isnull(s):
            message_subject += f', {s}'
    
    # Building the email file name attachment.
    file_name = create_attachment_file_name(
        user=user, filter_id=filter_id, state=state, city=city, category=category
        )

    # File path to save the attachment.
    file_path = output_dir+ file_name
    data_df.to_csv(file_path, sep=';', index=False)

    # Building the body message of email.
    message_body = "Segue abaixo e em anexo os imóveis encontrados para o filtro cadastrado. \n"
    message_body += data_df.to_string()

    # Sending email to receiver.
    send_email(
        receivers_email=[receiver_email],
        subject=message_subject,
        body_message=message_body,
        attachment_paths=[file_path]
    )

def send_email(
        receivers_email: list[str], 
        subject: str, 
        body_message: str, 
        attachment_paths: list[str] = [],
        host: str = 'smtp.gmail.com', port: int = 587, 
        sender_email: str =  "vpzleiloes@gmail.com",
        password: str = None
        ) -> None:
    """
    Function to send email from python.

    Parameters
    ----------
    receivers_email : list[str]
        Emails of the receivers
    subject : str
        Subject of the email
    body_message : str
        Body message of the email
    attachment_paths : list[str], optional
        File paths of attachments, by default []
    host : str, optional
        SMTP host of the sender email, by default 'smtp.gmail.com'
    port : int, optional
        Port of the SMTP of the sender email, by default 587
    sender_email : str, optional
        Sender email, by default "vpzleiloes@gmail.com"
    password : str, optional
        Password of the sender email, by default None
    """

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

def create_attachment_file_name(
        user: str,
        filter_id: int,
        state: str = None,
        city: str = None,
        category: str = None
        ) -> str:
    """
    Auxiliary function to generate the file name of attachment.

    Parameters
    ----------
    user : str
        The user that wants to receive the email with the filtered data.
    filter_id : int
        FilterId of this data filtered.
    state : str, optional
        State of the filter, by default None
    city : str, optional
        City of the filter, by default None
    category : str, optional
        Category of the filter, by default None

    Returns
    -------
    str
        File name of the attachment
    """
    
    # Building the attachment file name with not null information.
    file_name= f'Filtro_{filter_id}_{user}'
    for s in (state, city, category):
        if not pd.isnull(s):
            file_name += f'_{s}'

    file_name += '.csv'

    return file_name