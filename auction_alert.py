# -*- coding: utf-8 -*-
"""
Main scritp to execute the auction alert notifications.

"""

# Preventing __pycache__
import sys
sys.dont_write_bytecode = True

# Imports
import os
import re
import pandas as pd

# Project Imports
from functions.data_acquisition import (get_auctions_data, filter_data)
from functions.email_sender import send_action_notification, create_attachment_file_name

# Getting the project folder by the file execution.
script_dir = os.path.abspath(__file__)

# Replacing '\' for '/', because '\' is an escape character.
script_dir = re.sub(pattern = '\\\\', repl = '/', string = script_dir)

# Removing the file name and just keeping the project's folder name.
script_dir = re.sub(pattern="auction_alert.*", repl = "auction_alert/", string = script_dir)

# Data dir
data_dir = script_dir + '/data/'

# Seting as Working Directory the project's folder.
os.chdir(script_dir)

# Reading saved users.
users = pd.read_csv(data_dir+'users.csv')

# Reading saved filters.
filters = pd.read_csv(data_dir+'filters.csv')

# Getting the users and filters to send notifications.
setups =  users.merge(filters, on='UserId', how='inner')

# Using for to not compromise the Memory of the computer when the script is running.
# It can be paralelized with and pandas.apply or map() but it can be memory expensive with many filters/users.
for k in range(setups.shape[0]):
    xrow = setups.loc[k]
    data = get_auctions_data(state=xrow.State)

    # Filtering Data based on conditions.
    data = filter_data(
        data_df=data,
        city=xrow.City,
        category=xrow.Category,
        lower_price=xrow.LowerPrice,
        upper_price=xrow.UpperPrice,
        modality=xrow.Modality
        )

    # Checking if there is data to send in email.
    if not data.empty:
        output_dir = script_dir+'outputs/'
        file_name = create_attachment_file_name(
            user=xrow.UserName,
            filter_id=xrow.FilterId,
            state=xrow.State,
            city=xrow.City,
            category=xrow.Category
            )

        file_path = output_dir+file_name

        # If this email was already sent in the past check if there is any update in the data.
        if (os.path.exists(file_path) & xrow.OnlyUpdates):
            old_data = pd.read_csv(file_path, sep=';')
            
            # If it has updates send new email.
            send_data = not old_data.equals(data)
        else:
            # If is the first time sending data for this filter automatically sends the email.
            send_data = True

        if send_data:
            send_action_notification(
                data_df=data,
                output_dir=script_dir+'outputs/',
                user=xrow.UserName,
                filter_id=xrow.FilterId,
                receiver_email=xrow.UserEmail,
                state=xrow.State,
                city=xrow.City,
                category=xrow.Category
            )