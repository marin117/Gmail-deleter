from apiclient import errors
from tqdm import tqdm
import os
import base64
import email
from email.mime.text import MIMEText
from google_client import GoogleClient


class GmailHandler:
    def __init__(self, secret_file_path, arguments):
        self.google_client = GoogleClient(secret_file_path, arguments)

    def delete_message(self, user_id="me", msg_id=None):
        """Moves the message with the given msg_id to the trash folder.

        Args:
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msg_id: ID of the message to delete.

        Returns:
            A response from the server.
        """
        if msg_id is not None:
            try:
                response = (
                    self.google_client.service.users()
                    .messages()
                    .trash(userId=user_id, id=msg_id)
                    .execute()
                )
                return response
            except errors.HttpError as error:
                print("An error occurred: %s" % error)

    def delete_message_perm(self, user_id="me", msg_id=None):
        """Completely deletes a message (instead of moving it to trash) with the given msg_id.

        Args:
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msg_id: ID of the message to delete.

        Returns:
            A response from the server. It contains an empty body if successful.
        """
        if msg_id is not None:
            try:
                response = (
                    self.google_client.service.users()
                    .messages()
                    .delete(userId=user_id, id=msg_id)
                    .execute()
                )
                return response
            except errors.HttpError as error:
                print("An error occurred: %s" % error)

    def get_labels(self, user_id="me"):
        """Get a list of all labels in the user's mailbox.

        Args:
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.

        Returns:
        A list of all Labels in the user's mailbox.
        """
        label_result = (
            self.google_client.service.users().labels().list(userId=user_id).execute()
        )
        labels = label_result.get("labels", [])
        return labels

    def list_messages_with_label(self, user_id="me", label_ids=None):
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
        if label_ids is None:
            label_ids = []

        try:
            response = (
                self.google_client.service.users()
                .messages()
                .list(userId=user_id, labelIds=label_ids)
                .execute()
            )
            if "messages" in response:
                for message in response["messages"]:
                    yield message

            while "nextPageToken" in response:
                page_token = response["nextPageToken"]
                response = (
                    self.google_client.service.users()
                    .messages()
                    .list(userId=user_id, labelIds=label_ids, pageToken=page_token)
                    .execute()
                )
                if "messages" in response:
                    for message in response["messages"]:
                        yield message
        except errors.HttpError as error:
            print("An error occurred: %s" % error)

    def list_messages_matching_query(self, user_id="me", query=None):
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
        if query is not None:
            try:
                response = (
                    self.google_client.service.users()
                    .messages()
                    .list(userId=user_id, q=query)
                    .execute()
                )
                if "messages" in response:
                    for message in response["messages"]:
                        yield message

                while "nextPageToken" in response:
                    page_token = response["nextPageToken"]
                    response = (
                        self.google_client.service.users()
                        .messages()
                        .list(userId=user_id, q=query, pageToken=page_token)
                        .execute()
                    )
                    for message in response["messages"]:
                        yield message
            except errors.HttpError as error:
                print("An error occurred: %s" % error)

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
            message = (
                self.google_client.service.users()
                .messages()
                .get(userId=user_id, id=msg_id)
                .execute()
            )

            """print('Message snippet: %s' % message['snippet'])"""

            return message
        except errors.HttpError as error:
            print("An error occurred: %s" % error)

    def get_sender(self, message, interest):
        """Get sender of an email.

        Args:
                message: Email returned form get_message function.

        Returns:
                The sender of a given message.
        """
        for sender in message["payload"]["headers"]:
            if sender["name"].lower() == interest.lower():
                sender_name = sender["value"].split(" ")
                for values in sender_name:
                    if "@" in values:
                        if "<" in values:
                            value = values.lstrip("<")
                            value = value.rstrip(">")
                            return value
                        return values

    def download_message(self, user_id="me", msg_id=None, download_dir="downloads"):
        """Downloads a single message with attachments to local storage."""

        if msg_id is None:
            return "Message ID is None."

        try:

            # Get the full message

            message = (
                self.google_client.service.users()
                .messages()
                .get(userId=user_id, id=msg_id, format="full")
                .execute()
            )

            # Create or check the download directory

            if not os.path.exists(download_dir):

                os.makedirs(download_dir)

            # Extract message headers

            headers = message.get("payload", {}).get("headers", [])

            subject = next(
                (
                    header["value"]
                    for header in headers
                    if header["name"].lower() == "subject"
                ),
                "No Subject",
            )

            date = next(
                (
                    header["value"]
                    for header in headers
                    if header["name"].lower() == "date"
                ),
                "Unknown Date",
            )

            cleaned_subject = "".join([c if c.isalnum() else "_" for c in subject])

            filename_prefix = f"{download_dir}/{cleaned_subject}_{msg_id}"

            # Save metadata (subject, date)

            with open(f"{filename_prefix}.meta.txt", "w") as meta_file:

                meta_file.write(f"Subject: {subject}\n")

                meta_file.write(f"Date: {date}\n\n")

                meta_file.write(
                    f"Snippet: {message.get('snippet', 'No snippet available.')}\n"
                )

            # Download attachments and save

            self._process_message_parts(
                message.get("payload", {}), filename_prefix, msg_id
            )

            return f"Message {msg_id} downloaded successfully to {filename_prefix}."

        except errors.HttpError as error:

            return f"Error downloading message {msg_id}: {error}"

    def _process_message_parts(self, payload, filename_prefix, msg_id):
        """Processes parts of a message recursively to download attachments."""

        if "parts" in payload:

            for part in payload["parts"]:

                self._process_message_parts(part, filename_prefix)

        # Download attachments

        if payload.get("filename"):

            attachment_id = payload.get("body", {}).get("attachmentId")

            if attachment_id:

                attachment = (
                    self.google_client.service.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=msg_id, id=attachment_id)
                    .execute()
                )

                data = base64.urlsafe_b64decode(attachment["data"])

                with open(
                    f"{filename_prefix}_{payload['filename']}", "wb"
                ) as attachment_file:

                    attachment_file.write(data)

    def forward_message(self, user_id="me", msg_id=None, to_email=None):
        """Forwards a message to another email address."""

        if msg_id is None or to_email is None:

            return "Message ID or recipient email is None."

        try:

            # Get the raw message

            raw_message = (
                self.google_client.service.users()
                .messages()
                .get(userId=user_id, id=msg_id, format="raw")
                .execute()["raw"]
            )

            # Create and send forward message

            forward_payload = {
                "raw": self._create_forward_message(raw_message, to_email)
            }

            self.google_client.service.users().messages().send(
                userId=user_id, body=forward_payload
            ).execute()

            return f"Message {msg_id} forwarded successfully to {to_email}."

        except errors.HttpError as error:

            return f"Error forwarding message {msg_id}: {error}"

    def _create_forward_message(self, raw_message, to_email):
        """Creates a forward message from raw email content."""

        msg = MIMEText("Forwarding email content")
        msg["To"] = to_email
        msg["From"] = "me"
        msg["Subject"] = "FWD: Email content"
        encoded_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        return encoded_msg


class GmailBulkHandler(GmailHandler):
    BATCH_SIZE = 1000

    def delete_messages_perm(self, user_id="me", msgs=None):
        """Permanently deletes the messages.

        Args:
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            msgs: Messages to delete.

        Returns:
            None
        """
        if msgs is None:
            msgs = []

        msg_ids = []
        for msg in tqdm(msgs):
            msg_ids.append(msg["id"])
            if len(msg_ids) == self.BATCH_SIZE:
                self.google_client.service.users().messages().batchDelete(
                    userId=user_id, body={"ids": msg_ids}
                ).execute()
                msg_ids = []
        # Check and delete the last batch.
        if msg_ids:
            self.google_client.service.users().messages().batchDelete(
                userId=user_id, body={"ids": msg_ids}
            ).execute()
