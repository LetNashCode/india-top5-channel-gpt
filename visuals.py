"""
Fetches royalty-free stock video clips from Pixabay matching each item's
visual_keywords. Falls back to a solid-color card if no video match is
found (handled in assemble.py).
"""
import os
import requests

PIXABAY_SEARCH_URL = "https://pixabay.com/api/videos/"


def find_video_clip(keywords: list, orientation: str = "portrait") -> str | None:
    """Search Pixabay for a matching video, return the best-quality video
    URL, or None if nothing suitable was found."""
    query = " ".join(keywords)
    params = {
        "key": os.environ["PIXABAY_API_KEY"],
        "q": query,
        "video_type": "film",
        "per_page": 5,
    }
    resp = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    hits = data.get("hits", [])
    if not hits:
        return None

    video = hits[0]
    videos = video.get("videos", {})
    for tier in ("large", "medium", "small", "tiny"):
        if tier in videos and videos[tier].get("url"):
            return videos[tier]["url"]
    return None


def download_file(url: str, out_path: str) -> str:
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    with open(out_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    return out_path


def fetch_visuals_for_script(script: dict, config: dict, workdir: str) -> list:
    """Returns a list of local file paths (video clips), one per item, in order.
    If a search comes up empty, returns None for that slot so assemble.py can
    fall back to a solid-color/text card instead of crashing the run."""
    os.makedirs(workdir, exist_ok=True)
    orientation = config["visuals"]["orientation"]
    clip_paths = []
    for item in script["items"]:
        url = find_video_clip(item["visual_keywords"], orientation)
        if url is None:
            clip_paths.append(None)
            continue
        out_path = os.path.join(workdir, f"visual_{item['rank']}.mp4")
        download_file(url, out_path)
        clip_paths.append(out_path)
    return clip_paths
