# Gmail-deleter

Getting started
---------------

This script will help you delete unnecessary emails on gmail. It will provide you with options to delete all emails, emails from certain category and emails from a certain user . It also has additional features for emptying trash, deleteting spam emails, getting statistics for email size, or displaying frequency of sent/received emails to/from a certain user.


Prerequisites
-------------

 - Python
 - The [pip](https://pypi.python.org/pypi/pip) package managment tool for Python
 - Access to Internet and a web browser
 - A Google account with Gmail account enabled
 - matplotlib for Python 


Turn on Gmail API
-----------------

Follow the [instructions](https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name)

Installation
------------

 - Optional: Create a virtual environment 
 
 - Run: 
   
   `pip install --upgrade google-api-python-client`
    

(Check requirements.txt for additional informations about requirments for installation)

Usage
-----

 - Copy json file generated from Gmail API to the repository directory 


Run script with:

`python gmail-delete.py`

You can add extra options -s or --secret with a path to your "credentials.json" file.

`python gmail-delete.py -s credentials.json`

The script provides the following options:  
 -deletion of all messages  
 -deletion of all messages from a certain category (i.e. Promotions, Forums, Social...)  
 -deletion of all messages from a certain user  
 -emptying trash  
 -emptying spam  
 
If one of the first three options are selected, those messages will be moved to the trash.
