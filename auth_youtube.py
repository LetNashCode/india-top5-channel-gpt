"""
Run this ONCE on your own computer (not in CI) to authorize the pipeline
to upload to your YouTube channel. It opens a browser for you to log in
and approve access, then saves token.json.

Usage:
    python auth_youtube.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)
    with open("token.json", "w") as f:
        f.write(creds.to_json())
    print("Saved token.json — copy its contents into the YOUTUBE_TOKEN_JSON GitHub secret.")

if __name__ == "__main__":
    main()
