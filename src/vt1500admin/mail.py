
import os
import pickle

# Gmail API utils
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# for encoding/decoding messages in base64
from base64 import urlsafe_b64decode, urlsafe_b64encode
# for dealing with attachement MIME types
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type
from django.conf import settings
from django.templatetags.static import static

from djui.settings import STATIC_DIR

# Request all access (permission to read/send/receive emails, manage the inbox, and more)
SCOPES = ['https://mail.google.com/']
our_email = 'admin@unio.vote'

def gmail_authenticate():
    creds = None
    print(settings.BASE_DIR)

    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time

    google_token_path = os.path.join(STATIC_DIR, 'token.pickle')
    google_cred_path = os.path.join(STATIC_DIR, 'credentials.json')
    if os.path.exists(google_token_path):
        with open(google_token_path, "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(google_cred_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open(google_token_path, "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service
# service = gmail_authenticate()

def build_message(destination, obj, body, attachments=[]):
    # if not attachments: # no attachments given
    message = MIMEText(body)
    message['to'] = destination
    message['from'] = "admin@unio.vote"
    message['subject'] = obj
    # else:
    #     message = MIMEMultipart()
    #     message['to'] = destination
    #     message['from'] = our_email
    #     message['subject'] = obj
    #     message.attach(MIMEText(body))
    #     for filename in attachments:
    #         add_attachment(message, filename)
    return {'raw': urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, destination, obj, body, attachments=[]):
    return service.users().messages().send(
      userId="me",
      body=build_message(destination, obj, body, attachments)
    ).execute()

# test send email
# send_message(service, "nejadgholim@gmail.com", "ELECTION NOTICE", 
#             "Hello Arnaud, the bad news is google email service that is the best costs about $30 per month. We can unsubscribe it later." )
