from __future__ import print_function

import os

import httplib2
from apiclient import discovery
from oauth2client import client, tools
from oauth2client.file import Storage


SCOPES = 'https://mail.google.com'
APPLICATION_NAME = 'Gmail API Python'


class GoogleClient:
    def __init__(self, secret_file_path, arguments):
        """
        Constructor for GoogleClient object which calls Google mail API.
        """
        self.credentials = self.get_credentials(secret_file_path, arguments)
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=self.http)

    def get_credentials(self, secret_file_path, arguments):
        """
        Gets valid user credentials from storage.

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
            flow = client.flow_from_clientsecrets(secret_file_path, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if arguments:
                credentials = tools.run_flow(flow, store, arguments)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def build_service(self):
        """
        Build a Gmail service object.

        Args:
          credentials: OAuth 2.0 credentials.

        Returns:
          Gmail service object.
        """
        http = httplib2.Http()
        http = self.credentials.authorize(http)
        return discovery.build('gmail', 'v1', http=http)