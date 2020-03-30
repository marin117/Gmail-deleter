
from __future__ import print_function
import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors
from apiclient.discovery import build

import matplotlib.pyplot as plt
import collections

from gmail_handler import GmailHandler
import argparse


try:
    arguments = argparse.ArgumentParser(parents=[tools.argparser], description='Mass mail deleter for Gmail')
    arguments.add_argument('-s', '--secret', type=str, help='Path to the Google client secret json', required=False)
except ImportError:
    arguments = None


def main():
    args = arguments.parse_args()
    secret_file_path = args.secret

    gmail = GmailHandler(secret_file_path, args)

    while True:
        print("""
1. Delete all messages
2. Delete messages from category
3. Delete messages from specific user
4. Empty trash
5. Empty spam
6. Statistics
7. Batch delete messages from category (EXPERIMENTAL!!!)
8. Exit

        """)
        try:
            choice = int(input('Choose an option: '))
            if choice == 1:
                messages = gmail.list_messages_matching_query(
                    'me', 'label:all')
                for message in messages:
                    delete = gmail.delete_message_perm('me', message['id'])
            elif choice == 2:
                labels = gmail.get_labels('me')
                for i, label in enumerate(labels):
                    print(str(i+1) + ': ' + label['name'])
                try:
                    label_choice = int(input('Choose label for deletion: '))
                    if label_choice <= 0 or label_choice >= len(labels) + 1:
                        print("Invalid input! Try again")
                        continue
                except ValueError:
                    print('Invalid input! Try again')
                    continue
                for message in gmail.list_messages_with_label('me', labels[label_choice-1]['id']):
                    delete = gmail.delete_message('me', message['id'])
            elif choice == 3:
                user_choice = str(
                    input('Choose user whose messages you want to delete: '))
                for message in gmail.list_messages_matching_query('me', 'from:' + user_choice):
                    delete = gmail.delete_message('me', message['id'])
            elif choice == 4:
                for message in gmail.list_messages_with_label('me', 'TRASH'):
                    delete = gmail.delete_message_perm('me', message['id'])
            elif choice == 5:
                for message in gmail.list_messages_with_label('me', 'SPAM'):
                    delete = gmail.delete_message_perm('me', message['id'])
            elif choice == 6:
                print("""
1. Statistics for received mail
2. Statistics for sent mail
3. Statistics for received mail size
4. Statistics for sent mail size
        """)

                try:
                    statistic_choice = int(input('Choose an option: '))
                    if statistic_choice == 1:
                        gmail.get_statistic_for_user('me', 'INBOX', 'FROM')
                    elif statistic_choice == 2:
                        gmail.get_statistic_for_user('me', 'SENT', 'TO')
                    elif statistic_choice == 3:
                        gmail.get_statistics_for_mail_size('me', 'INBOX')
                    elif statistic_choice == 4:
                        gmail.get_statistics_for_mail_size('me', 'SENT')
                    else:
                        sys.exit(1)
                except ValueError:
                    print('Invalid input! Try again')
            elif choice == 7:
                labels = gmail.get_labels('me')
                for i, label in enumerate(labels):
                    print(str(i+1) + ': ' + label['name'])
                try:
                    label_choice = int(input('Choose label for deletion: '))
                    if label_choice <= 0 or label_choice >= len(labels) + 1:
                        print("Invalid input! Try again")
                        continue
                except ValueError:
                    print('Invalid input! Try again')
                    continue
                messages = gmail.list_messages_with_label('me', labels[label_choice-1]['id'])
                msg_ids = [msg['id'] for msg in messages]
                delete = gmail.batch_delete('me', msg_ids)
            else:
                sys.exit(1)
        except ValueError:
            print('Invalid input! Try again')


if __name__ == '__main__':
    main()
