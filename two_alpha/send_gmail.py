import pickle
import os.path
import logging
import logging

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from apiclient import errors, discovery

SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'

logger = logging.getLogger(__name__)

class SendGmail:
    def get_service():
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials = creds, cache_discovery = False)
        return service

    def send_message(sender, to, msgPlain, subject = ""):
        """Send an email message.

        Args:
            service: Authorized Gmail API service instance.
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.

        Returns:
            Sent Message.
        """
        def create_message(sender, to, subject, message_text):
            """Create a message for an email.

            Args:
                sender: Email address of the sender.
                to: Email address of the receiver.
                subject: The subject of the email message.
                message_text: The text of the email message.

            Returns:
                An object containing a base64url encoded email object.
            """
            message = MIMEText(message_text)
            message['to'] = to
            message['from'] = sender
            message['subject'] = subject
            print(message)
            return { 'raw' : base64.urlsafe_b64encode(message.as_bytes()).decode() }

        try:
            service = SendGmail.get_service()
            msg = create_message(sender, to, subject, msgPlain)
            msg = (service.users().messages().send(userId = "me", body = msg)
                       .execute())

            logger.info('Message Id: %s' % msg['id'])
            return msg
        except (errors.HttpError, error) as e:
            logger.error('An error occurred: %s' % e)

