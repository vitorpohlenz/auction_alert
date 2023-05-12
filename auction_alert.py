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
from data_acquisition import (get_auctions_data, filter_data)
from email_sender import send_action_notification

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

    data = filter_data(
        data_df=data,
        city=xrow.City,
        category=xrow.Category,
        lower_price=xrow.LowerPrice,
        upper_price=xrow.UpperPrice,
        modality=xrow.Modality
        )
    
    if not data.empty:
        send_action_notification(
            data_df=data,
            output_dir=script_dir+'outputs/',
            user=xrow.UserName,
            filter_id=xrow.FilterId,
            receiver_email=xrow.UserEmail
        )