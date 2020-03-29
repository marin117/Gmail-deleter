from google_client import GoogleClient
from urllib.error import HTTPError
import collections
import json
from apiclient import errors

class GmailHandler:
    def __init__(self, secret_file_path, arguments):
        self.google_client = GoogleClient(secret_file_path, arguments)
        pass


    def delete_message(self, user_id, msg_id):
        try:
            response = self.google_client.service.users().messages().trash(userId=user_id, id=msg_id).execute()
            return response
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def delete_message_perm(self, user_id, msg_id):
        try:
            response = self.google_client.service.users().messages().delete(
                userId=user_id, id=msg_id).execute()
            return response
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def get_labels(self, user_id):
        label_result = self.google_client.service.users().labels().list(userId=user_id).execute()
        labels = label_result.get('labels', [])
        return labels

    def list_messages_with_label(self, user_id, label_ids=[]):
        """List all Messages of the user's mailbox with labelIds applied.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          labelIds: Only return Messages with these labelIds applied.

        Returns:
          List of Messages that have all required Labels applied. Note that the
          returned list contains Message IDs, you must use get with the
          appropriate id to get the details of a Message.
        """
        try:
            response = self.google_client.service.users().messages().list(userId=user_id,
             labelIds=label_ids).execute()
            if 'messages'in response:
                for message in response['messages']:
                    yield message

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.google_client.service.users().messages().list(userId=user_id,
                 labelIds=label_ids,
                 pageToken=page_token).execute()
                if 'messages'in response:
                    for message in response['messages']:
                        yield message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def list_messages_matching_query(self, user_id, query=''):
        """List all Messages of the user's mailbox matching the query.

        Args:
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
            response = self.google_client.service.users().messages().list(userId=user_id,
                                                       q=query).execute()
            if 'messages' in response:
                for message in response['messages']:
                    yield message

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.google_client.service.users().messages().list(userId=user_id, q=query,
                                                           pageToken=page_token).execute()
                for message in response['messages']:
                        yield message

        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def get_message(self, user_id, msg_id):
        """Get a Message with given ID.

        Args:
          user_id: User's email address. The special value "me"
          can be used to indicate the authenticated user.
          msg_id: The ID of the Message required.

        Returns:
          A Message.
        """
        try:
            message = self.google_client.service.users().messages().get(userId=user_id, id=msg_id).execute()

            """print('Message snippet: %s' % message['snippet'])"""

            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def get_sender(self, message, interest):
        """Get sender of an email.

        Args:
                message: Email returned form get_message function.

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
                            return value
                        return values


    def get_statistic_for_user(self, user_id, decision, interest):
        """Get all the statistic for sent/received mail based on users choice.

        Args:
                user_id: User's email address. The special value "me".
                decision: 'INBOX' or 'SENT'. Defines if we want statistics for sent or received mail.
                interest: 'FROM' or 'To'. Based on the 'decision' arg, it tells the 'get_sender' if we are
                            interested in the 'FROM' or 'To' field of email headers

        Returns:
                Nothing.
        """
        statistic = dict()
        messages = self.list_messages_with_label(user_id, decision)
        for message in messages:
            message_info = self.get_message(user_id, message['id'])
            sender = self.get_sender(message_info, interest)
            if sender in statistic:
                statistic[sender] += 1
            else:
                statistic[sender] = 1
        #print(statistic)
        plt.bar(statistic.keys(), statistic.values())
        plt.xticks(rotation = 'vertical')
        plt.tight_layout()
        plt.show()

    def get_statistics_for_mail_size(self, user_id, label_choice):
        """Get the statistic for sent/received mail based on mail size.

        Args:
                user_id: User's email address. The special value "me".
                label_choice: Mailbox we are interested in. Usually 'INBOX' or 'SENT'.

        Returns:
                Nothing.
        """
        statistic = collections.OrderedDict ()
        messages = self.list_messages_matching_query(user_id, ('label:' + label_choice + ' smaller_than:1mb'))
        statistic['<1mb'] = len(messages)
        messages = self.list_messages_matching_query(user_id, ('label:' + label_choice + ' smaller_than:5mb' + ' larger:1mb'))
        statistic['1mb<x<5mb'] = len(messages)
        messages = self.list_messages_matching_query(user_id, ('label:' + label_choice + ' smaller_than:10mb' + ' larger:5mb'))
        statistic['5mb<x<10mb'] = len(messages)
        messages = self.list_messages_matching_query(user_id, ('label:' + label_choice + ' smaller_than:25mb' + ' larger:10mb'))
        statistic['10mb<x<25mb'] = len(messages)
        messages = self.list_messages_matching_query(user_id, ('label:' + label_choice + ' smaller_than:50mb' + ' larger:25mb'))
        statistic['25mb<x<50mb'] = len(messages)
        messages = self.list_messages_matching_query(user_id, ('label:' + label_choice + ' larger:50mb'))
        statistic['>50mb'] = len(messages)
        #print (statistic)
        plt.bar(statistic.keys(), statistic.values())
        plt.xticks(rotation = 'vertical')
        plt.tight_layout()
        plt.show()

    def get_message_ids_query(self, user_id, query=''):
        try:
            response = self.google_client.service.users().messages().list(userId=user_id,
                                                       q=query).execute()
            if 'messages' in response:
                message_ids = []
                for message in response['messages']:
                    message_ids.append(message['id'])
                yield message_ids

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.google_client.service.users().messages().list(userId=user_id, q=query,
                                                           pageToken=page_token).execute()
                message_ids = []
                for message in response['messages']:
                    message_ids.append(message['id'])
                yield message_ids

        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def get_message_ids_label(self, user_id, label_ids=[]):
        try:
            response = self.google_client.service.users().messages().list(userId=user_id,
             labelIds=label_ids).execute()
            if 'messages'in response:
                message_ids = []
                for message in response['messages']:
                    message_ids.append(message['id'])
                yield message_ids

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = self.google_client.service.users().messages().list(userId=user_id,
                 labelIds=label_ids,
                 pageToken=page_token).execute()
                if 'messages'in response:
                    message_ids = []
                    for message in response['messages']:
                        message_ids.append(message['id'])
                    yield message_ids
        except errors.HttpError as error:
            print('An error occurred: %s' % error)

    def batch_delete(self, user_id, message_ids=[]):
        lista = json.dumps({'ids': message_ids})
        self.google_client.service.users().messages().batchDelete(userId=user_id, body=lista)
