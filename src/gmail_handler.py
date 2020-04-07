from google_client import GoogleClient
import collections

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