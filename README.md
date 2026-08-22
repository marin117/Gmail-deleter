# Gmail-deleter

Getting started
---------------

This script will help you delete unnecessary emails on gmail. It will provide you with options to delete all emails, emails from certain category and emails from a certain user . It also has additional features for emptying trash, deleting spam emails, getting statistics for email size, or displaying frequency of sent/received emails to/from a certain user.


Prerequisites
-------------

 - Python 3.9 or newer
 - The [uv](https://docs.astral.sh/uv/getting-started/installation/) Python package manager
 - Access to Internet and a web browser
 - A Google account with Gmail account enabled


Turn on Gmail API
-----------------

Follow the [instructions](https://developers.google.com/gmail/api/quickstart/python#step_1_turn_on_the_api_name)

Installation
------------

Install the locked dependencies:

`uv sync --locked`

Usage
-----

 - Copy json file generated from Gmail API to the repository directory


Run the script from the repository directory with:

`uv run gmail-deleter`

You can add extra options -s or --secret with a path to your "credentials.json" file.

`uv run gmail-deleter -s credentials.json`

The script provides the following options:
 - delete all messages
 - delete all messages from a certain category (i.e. Promotions, Forums, Social...)
 - delete all messages from a certain user
 - clear trash
 - clear spam
 - delete messages matching custom filter

**WARNING:** All messages will be deleted permanently (**not** moved to **Trash**).
