import os
import requests

API_URL = "https://freesound.org/apiv2/search/text/"


def download_sfx(script, workdir):
    os.makedirs(workdir, exist_ok=True)

    api_key = os.environ["FREESOUND_API_KEY"]

    sfx_paths = []

    for keyword in script.get("sfx_search", []):

        print("=" * 80)
        print(f"💥 Searching SFX: {keyword}")
        print("=" * 80)

        params = {
            "query": keyword,
            "fields": "id,name,previews",
            "filter": "duration:[0 TO 15]",
            "sort": "score",
            "token": api_key,
        }

        response = requests.get(
            API_URL,
            params=params,
            timeout=60,
        )

        response.raise_for_status()

        results = response.json().get("results", [])

        if not results:
            print(f"No SFX found for '{keyword}'")
            continue

        sound = results[0]

        preview_url = (
            sound.get("previews", {}).get("preview-hq-mp3")
            or sound.get("previews", {}).get("preview-lq-mp3")
        )

        if not preview_url:
            continue

        path = os.path.join(
            workdir,
            f"{keyword.replace(' ', '_')}.mp3",
        )

        audio = requests.get(
            preview_url,
            timeout=120,
        )

        audio.raise_for_status()

        with open(path, "wb") as f:
            f.write(audio.content)

        print(f"Downloaded: {keyword}")

        sfx_paths.append(path)

    return sfx_paths
