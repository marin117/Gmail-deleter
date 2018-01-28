
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


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python'


def GetCredentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-delete.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def BuildService(credentials):
    """Build a Gmail service object.

    Args:
      credentials: OAuth 2.0 credentials.

    Returns:
      Gmail service object.
    """
    http = httplib2.Http()
    http = credentials.authorize(http)
    return build('gmail', 'v1', http=http)


def DeleteMessage(service, user_id, msg_id):
    try:
        response = service.users().messages().trash(userId=user_id, id=msg_id).execute()
        return response
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def DeleteMessagePerm(service, user_id, msg_id):
    try:
        response = service.users().messages().delete(
            userId=user_id, id=msg_id).execute()
        return response
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def ListMessagesWithLabels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      label_ids: Only return Messages with these labelIds applied.

    Returns:
      List of Messages that have all required Labels applied. Note that the
      returned list contains Message IDs, you must use get with the
      appropriate id to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                                   labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                       labelIds=label_ids,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      query: String used to filter messages returned.
      Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
      List of Messages that match the criteria of the query. Note that the
      returned list contains Message IDs, you must use get with the
      appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      msg_id: The ID of the Message required.

    Returns:
      A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        """print('Message snippet: %s' % message['snippet'])"""

        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def GetSender(message, interest):
    """Get sender of an email.

    Args:
            message: Email returned form GetMessage function.

    Returns:
            The sender of a given message.
    """
    for sender in message['payload']['headers']:
        if sender['name'].lower() == interest.lower():
            sender_name = sender['value'].split(" ")
            for values in sender_name:
                if '@' in values:
                    if '<' in values:
                        value = values.lstrip('<')
                        value = value.rstrip('>')
                        #print(value)
                        return value
                    #print(values)
                    return values


def GetStatisticForUser(service, user_id, decision, interest):
    """Get all the statistic for sent/received mail based on users choice.

    Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me".
            decision: 'INBOX' or 'SENT'. Defines if we want statistics for sent or received mail.
            interest: 'FROM' or 'To'. Based on the 'decision' arg, it tells the 'GetSender' if we are
                        interested in the 'FROM' or 'To' field of email headers

    Returns:
            Nothing.
    """
    statistic = dict()
    messages = ListMessagesWithLabels(
        service, user_id, decision)
    for message in messages:
        message_info = GetMessage(
            service, user_id, message['id'])
        sender = GetSender(message_info, interest)
        if sender in statistic:
            statistic[sender] += 1
        else:
            statistic[sender] = 1
    #print(statistic)
    plt.bar(statistic.keys(), statistic.values())
    plt.xticks(rotation = 'vertical')
    plt.tight_layout()
    plt.show()

def GetStatisticForMailSize(service, user_id, label_choice):
    """Get the statistic for sent/received mail based on mail size.

    Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me".
            label_choice: Mailbox we are interested in. Usually 'INBOX' or 'SENT'.

    Returns:
            Nothing.
    """
    statistic = collections.OrderedDict ()
    messages = ListMessagesMatchingQuery(service, user_id, ('label:' + label_choice + ' smaller_than:1mb'))
    statistic['<1mb'] = len(messages)
    messages = ListMessagesMatchingQuery(service, user_id, ('label:' + label_choice + ' smaller_than:5mb' + ' larger:1mb'))
    statistic['1mb<x<5mb'] = len(messages)
    messages = ListMessagesMatchingQuery(service, user_id, ('label:' + label_choice + ' smaller_than:10mb' + ' larger:5mb'))
    statistic['5mb<x<10mb'] = len(messages)
    messages = ListMessagesMatchingQuery(service, user_id, ('label:' + label_choice + ' smaller_than:25mb' + ' larger:10mb'))
    statistic['10mb<x<25mb'] = len(messages)
    messages = ListMessagesMatchingQuery(service, user_id, ('label:' + label_choice + ' smaller_than:50mb' + ' larger:25mb'))
    statistic['25mb<x<50mb'] = len(messages)
    messages = ListMessagesMatchingQuery(service, user_id, ('label:' + label_choice + ' larger:50mb'))
    statistic['>50mb'] = len(messages)
    #print (statistic)
    plt.bar(statistic.keys(), statistic.values())
    plt.xticks(rotation = 'vertical')
    plt.tight_layout()
    plt.show()

def main():

    credentials = GetCredentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    while True:
        print("""
1. Delete all messages
2. Delete messages from category
3. Delete messages from specifed user
4. Empty trash
5. Empty spam
6. Statistics
7. Exit
        """)
        try:
            choice = int(input('Choose an option: '))
            if choice == 1:
                messages = ListMessagesMatchingQuery(
                    service, 'me', 'label:all')
                for message in messages:
                    delete = DeleteMessagePerm(service, 'me', message['id'])
            elif choice == 2:
                label_result = service.users().labels().list(userId='me').execute()
                labels = label_result.get('labels', [])
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
                messages = ListMessagesWithLabels(
                    service, 'me', labels[label_choice-1]['id'])
                for message in messages:
                    delete = DeleteMessage(service, 'me', message['id'])
            elif choice == 3:
                user_choice = str(
                    input('Choose user whose messages you want to delete: '))
                messages = ListMessagesMatchingQuery(
                    service, 'me', 'from:' + user_choice)
                for message in messages:
                    delete = DeleteMessage(service, 'me', message['id'])
            elif choice == 4:
                messages = ListMessagesWithLabels(
                    service, 'me', 'TRASH')
                for message in messages:
                    delete = DeleteMessagePerm(service, 'me', message['id'])
            elif choice == 5:
                messages = ListMessagesWithLabels(
                    service, 'me', 'SPAM')
                for message in messages:
                    delete = DeleteMessagePerm(service, 'me', message['id'])
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
                        GetStatisticForUser (service, 'me', 'INBOX', 'FROM')
                    elif statistic_choice == 2:
                        GetStatisticForUser (service, 'me', 'SENT', 'TO')
                    elif statistic_choice == 3:
                        GetStatisticForMailSize (service, 'me', 'INBOX')
                    elif statistic_choice == 4:
                        GetStatisticForMailSize (service, 'me', 'SENT')
                    else:
                        sys.exit(1)
                except ValueError:
                    print('Invalid input! Try again')

            else:
                sys.exit(1)
        except ValueError:
            print('Invalid input! Try again')


if __name__ == '__main__':
    main()
