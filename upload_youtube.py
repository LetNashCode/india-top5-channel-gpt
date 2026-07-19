"""
Uploads the finished video to YouTube via the YouTube Data API v3, using
a token generated once via auth_youtube.py.
"""
import json
import os

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def _get_credentials() -> Credentials:
    token_json = os.environ.get("YOUTUBE_TOKEN_JSON")
    if token_json:
        info = json.loads(token_json)
    else:
        with open("token.json") as f:
            info = json.load(f)
    return Credentials.from_authorized_user_info(info)


def upload_video(video_path: str, title: str, description: str, config: dict) -> str:
    creds = _get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    upload_cfg = config["upload"]
    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": upload_cfg.get("default_tags", []),
            "categoryId": upload_cfg.get("category_id", "24"),
        },
        "status": {
            "privacyStatus": upload_cfg.get("privacy_status", "public"),
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"Uploaded: https://www.youtube.com/shorts/{video_id}")
    return video_id
