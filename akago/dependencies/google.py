import base64
from contextlib import ExitStack
from email.message import EmailMessage
from io import BytesIO
from types import TracebackType
from typing import AsyncGenerator, Self, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from googleapiclient.http import MediaIoBaseDownload, MediaUpload

from akago.config import GOOGLE_ACCESS_TOKEN_PATH, GOOGLE_CLIENT_CREDENTIALS_PATH

_SCOPES = (
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.send",
)


def init_google_service() -> None:
    _get_credentials()


class GoogleService:
    def __init__(self, credentials: Credentials) -> None:
        self._stack = ExitStack()
        self._drive_service: Resource = self._stack.enter_context(
            build("drive", "v3", credentials=credentials)
        )
        self._mail_service: Resource = self._stack.enter_context(
            build("gmail", "v1", credentials=credentials)
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        return cast(bool, self._stack.__exit__(exc_type, exc_value, traceback))

    def close(self) -> None:
        self.__exit__(None, None, None)

    def download_file(self, id: str) -> bytes:
        file = BytesIO()
        request = self._drive_service.files().get_media(fileId=id)  # type: ignore
        downloader = MediaIoBaseDownload(file, request)
        done = False

        while done is False:
            _, done = downloader.next_chunk()

        return file.getvalue()

    def upload_file(self, filename: str, media: MediaUpload) -> str:
        file = (
            self._drive_service.files()  # type: ignore
            .create(body={"name": filename}, media_body=media, fields="id")
            .execute()
        )

        return file["id"]

    def send_email(self, message: EmailMessage) -> None:
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        body = {"raw": encoded_message}

        self._mail_service.users().messages().send(userId="me", body=body).execute()  # type: ignore


async def get_google_service() -> AsyncGenerator[GoogleService, None]:
    credentials = _get_credentials()
    service = GoogleService(credentials)

    yield service

    service.close()


def _get_credentials() -> Credentials:
    credentials: Credentials | None = None

    try:
        credentials = Credentials.from_authorized_user_file(
            GOOGLE_ACCESS_TOKEN_PATH, _SCOPES
        )
    except FileNotFoundError:
        pass

    if credentials is None or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CLIENT_CREDENTIALS_PATH, _SCOPES
            )
            credentials = cast(Credentials, flow.run_local_server(port=0))

        GOOGLE_ACCESS_TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")

    return credentials
