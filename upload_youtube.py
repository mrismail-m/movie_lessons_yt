import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_authenticated_service():
    """
    Constructs OAuth2 credentials from environment variables populated via GitHub Secrets.
    YOUTUBE_CLIENT_SECRET = the contents of client_secret.json
    YOUTUBE_OAUTH_TOKEN = the contents of token.json (contains refresh_token)
    """
    client_secret_json = os.environ.get("YOUTUBE_CLIENT_SECRET")
    oauth_token_json = os.environ.get("YOUTUBE_OAUTH_TOKEN")
    
    if not oauth_token_json or not client_secret_json:
        raise ValueError("Missing YOUTUBE_CLIENT_SECRET or YOUTUBE_OAUTH_TOKEN environment variables!")
        
    token_data = json.loads(oauth_token_json)
    client_data = json.loads(client_secret_json)
    
    # client_secret.json structure differs slightly depending on 'web' vs 'installed' app
    client_config = client_data.get("installed", client_data.get("web", {}))
    
    credentials = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=client_config.get("token_uri"),
        client_id=client_config.get("client_id"),
        client_secret=client_config.get("client_secret"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )
    
    return build("youtube", "v3", credentials=credentials)

def upload_video(video_path, title, description, category_id="24", privacy_status="private", publish_at=None):
    """Uploads the video using the YouTube Data API v3."""
    youtube = get_authenticated_service()
    
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }
    
    if publish_at:
        body["status"]["publishAt"] = publish_at
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )
    
    print(f"Uploading {video_path} to YouTube as '{title}'...")
    response = insert_request.execute()
    video_id = response.get("id")
    print(f"Upload successful! Video ID: {video_id}")
    return video_id
