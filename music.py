import os
import requests

API_URL = "https://freesound.org/apiv2/search/text/"


def download_music(script, workdir):
    os.makedirs(workdir, exist_ok=True)

    api_key = os.environ["FREESOUND_API_KEY"]

    query = script.get("music_search", "cinematic background")

    print("=" * 80)
    print("🎵 Searching Freesound")
    print(query)
    print("=" * 80)

    params = {
        "query": query,
        "fields": "id,name,previews,download,license",
        "filter": "duration:[20 TO 300]",
        "sort": "score",
        "token": api_key,
    }

    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        raise RuntimeError(f"No music found for: {query}")

    music = results[0]

    preview_url = (
        music.get("previews", {})
        .get("preview-hq-mp3")
        or music.get("previews", {})
        .get("preview-lq-mp3")
    )

    if not preview_url:
        raise RuntimeError("Music preview unavailable.")

    print(f"Selected: {music['name']}")

    path = os.path.join(workdir, "background.mp3")

    audio = requests.get(preview_url, timeout=120)
    audio.raise_for_status()

    with open(path, "wb") as f:
        f.write(audio.content)

    print(f"Saved: {path}")

    return path
