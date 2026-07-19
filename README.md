# Indian Top 5 — Fully Automated YouTube Shorts Pipeline

A "Nuke's Top 5"-style channel, adapted for an Indian audience (haunted places,
folklore, unsolved mysteries, urban legends). This pipeline does everything
end to end, on a schedule, with no manual steps once it's set up:

```
Topic idea  →  Script (5 items)  →  Voiceover (TTS)  →  Visuals  →
Video assembly (captions, music, 9:16)  →  Upload to YouTube (scheduled)
```

## How it runs automatically

It runs as a **GitHub Actions cron job** — free, and it runs even if your
laptop is off. Every run:
1. Picks a topic your channel hasn't covered yet (tracked in `used_topics.json`)
2. Generates a Top-5 script
3. Generates narration audio
4. Pulls matching stock visuals
5. Assembles a 9:16 Short with captions + background music
6. Uploads it to YouTube as a scheduled/public video

You only touch this repo when you want to change the niche, voice, or posting
frequency.

## One-time setup (about 30–45 minutes)

### 1. Get an Anthropic API key (for script writing)
- console.anthropic.com → Get API key → copy it.

### 2. Get a free Pexels API key (for stock visuals)
- pexels.com/api → sign up → copy your key. Free, no card needed.

### 3. Create a YouTube Data API v3 credential (for uploading)
- console.cloud.google.com → New Project
- Enable "YouTube Data API v3"
- OAuth consent screen → External → fill basic info → add your own Google
  account as a Test User
- Credentials → Create OAuth client ID → Desktop app → download the JSON,
  save it as `client_secret.json` in this folder
- Run `python auth_youtube.py` once on your own computer (not in CI) — it
  opens a browser, you approve access, and it saves `token.json`. Only needs
  to happen once; after that the pipeline reuses the token.

### 4. Add secrets to GitHub
In your repo: Settings → Secrets and variables → Actions → New repository
secret. Add:
- `ANTHROPIC_API_KEY`
- `PEXELS_API_KEY`
- `YOUTUBE_TOKEN_JSON` (paste the full contents of `token.json` from step 3)
- `YOUTUBE_CLIENT_SECRET_JSON` (paste the full contents of `client_secret.json`)

### 5. Push this folder to a GitHub repo
The workflow in `.github/workflows/publish.yml` is already set to run daily
at 14:00 UTC (7:30 PM IST) — edit the cron line to change frequency.

## Costs
- Anthropic API: pennies per script (~$0.01–0.03/video)
- Pexels: free
- TTS: uses free `edge-tts` (Microsoft Edge's free neural voices, includes
  Indian-English and Hindi voices) — $0 cost
- YouTube Data API: free, but capped at 10,000 quota units/day. An upload
  costs ~1,600 units, so you can safely publish **up to ~6 Shorts/day** on
  the free tier.

## Customizing
- Edit `config.yaml` — niche, language (English/Hindi/Hinglish), voice,
  posting time, video length, hashtags, whether videos go public immediately
  or as scheduled/private-until-date.
- Edit `topics.py` — the seed list of topic categories it draws from and
  expands on (haunted forts, cursed villages, unsolved Bollywood-era
  mysteries, etc.) — add/remove categories any time.

## Running one video manually (for testing)
```bash
pip install -r requirements.txt
python main.py --dry-run       # generates everything but skips upload
python main.py                 # generates and uploads
```

## Files
- `config.yaml` — all settings
- `topics.py` — topic bank + "already used" tracking
- `generate_script.py` — calls Claude to write the Top-5 script
- `tts.py` — turns the script into narration audio
- `visuals.py` — fetches matching stock video clips from Pexels
- `assemble.py` — stitches everything into a 9:16 MP4 with burned-in captions
- `upload_youtube.py` — uploads the finished video via the YouTube API
- `auth_youtube.py` — one-time OAuth login helper (run locally, not in CI)
- `main.py` — orchestrates the whole pipeline
- `.github/workflows/publish.yml` — the cron job that runs it automatically
