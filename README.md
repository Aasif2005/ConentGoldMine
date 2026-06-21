# ContentGoldmine — MVP (Content Mode)

Scans **Reddit + YouTube** for a niche and returns:
- **What to make** — demand-ranked topics people are asking about
- **Where to post** — communities ranked by activity

This is the lean MVP from the architecture. Two ways to run it:
1. **CLI** (fastest validation): `python run_cli.py "fitness"`
2. **Web app**: `uvicorn main:app --reload` then open http://localhost:8000

---

## 1. Setup

```bash
cd content-goldmine-mvp
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in your keys
```

## 2. Get your API keys (all have free tiers)

| Key | Where | Cost |
|-----|-------|------|
| `REDDIT_CLIENT_ID` / `SECRET` | https://www.reddit.com/prefs/apps → create app → type "script" | Free (100 queries/min) |
| `YOUTUBE_API_KEY` | https://console.cloud.google.com → enable "YouTube Data API v3" | Free (10k units/day) |
| `OPENAI_API_KEY` | https://platform.openai.com | ~$0.01 per scan (optional) |

> **No keys yet?** The app still runs — it just returns an empty result and tells you which keys are missing. Add Reddit first (it's the richest source).
>
> **No OpenAI key?** It automatically falls back to a keyword-based clustering so you can still see results for free.

## 3. Run it

```bash
# CLI — prints topics + communities to your terminal
python run_cli.py "fitness"

# Web — the prototype UI, now backed by real data
uvicorn main:app --reload
```

---

## Project structure

```
content-goldmine-mvp/
├─ main.py                 # FastAPI web server
├─ run_cli.py              # CLI entry point (no server needed)
├─ config.py               # loads .env
├─ collectors/
│  ├─ reddit_collector.py  # Reddit posts + comments (PRAW)
│  └─ youtube_collector.py # YouTube videos + comments
├─ analysis/
│  └─ analyzer.py          # clusters + scores topics (LLM or keyword fallback)
├─ core/
│  ├─ pipeline.py          # orchestrates a scan
│  └─ cache.py             # 24h file cache (saves your API quota)
└─ frontend/
   └─ index.html           # simple UI that calls /api/scan
```

## How a scan flows

```
niche → cache check → [Reddit + YouTube collectors] → analyzer (cluster+score) → rank communities → report (cached) → UI/CLI
```

## ⚠️ Validation note
Use the **CLI** to validate before building anything fancy. Run it for 5 niches, paste the output into a Google Doc, and show 5 potential customers. If they say "I'd pay for this" — *then* invest in the web app, accounts, and scaling.
