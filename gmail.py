import base64
import os
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_PATH = Path("credentials.json")
TOKEN_PATH = Path("gmail_token.json")
EMAIL = os.getenv("EMAIL")

credentials: Credentials | None = None

if EMAIL is None:
    raise ValueError(
        "Missing EMAIL environment variable. Add a `.env` file with your e-mail to the project"
    )

if TOKEN_PATH.exists():
    credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

if credentials is None or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        credentials = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")

try:
    service = build("gmail", "v1", credentials=credentials)
    message = EmailMessage()
    message["To"] = EMAIL
    message["From"] = EMAIL
    message["Subject"] = "Dokumenty cyfrowe – testowy e-mail"

    message.set_content("To jest wiadomość testowa")

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    body = {"raw": encoded_message}

    service.users().messages().send(userId="me", body=body).execute()

    print("E-mail sent")
except HttpError as error:
    print(f"An error occurred: {error}")
