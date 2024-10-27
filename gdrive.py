from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CREDENTIALS_PATH = Path("credentials.json")
TOKEN_PATH = Path("gdrive_token.json")

credentials: Credentials | None = None

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
    service = build("drive", "v3", credentials=credentials)

    file_metadata = {"name": "dane.md"}
    media = MediaFileUpload("dane.md", mimetype="text/markdown")

    service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    print("File uploaded")
except HttpError as error:
    print(f"An error occurred: {error}")
