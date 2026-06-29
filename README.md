# ContentGoldmine — Content Mode MVP

Scan any niche, read real YouTube **titles, views, likes & comments**, and get a
ranked list of what content to make next + where to post it.

## Project layout

```
content-goldmine-mvp/
  backend/                 ← all server code (MVC)
    app/
      models/              data + data sources
        config.py            env config (Reddit / YouTube / OpenRouter / OpenAI)
        schemas.py           pydantic request + ScanReport (API contract)
        cache.py             24h file cache
        youtube_source.py    YouTubeSource: titles + statistics + top comments
        reddit_source.py     RedditSource: posts + comments (empty if no creds)
      services/
        analyzer.py          Analyzer: clusters items into ranked topics
      controllers/
        scan_controller.py   ScanController: sources -> analyzer -> view
      views/
        serializers.py       builds the JSON response shape
      routes.py              FastAPI routes (POST /api/scan, GET /, GET /landing)
    main.py                  entrypoint: app = FastAPI(); include_router(router)
    run_cli.py               optional: scan from the terminal
    requirements.txt
    .env.example             copy to .env and fill in your keys
    .gitignore
  frontend/
    search.html              niche search page (served at /)
    landing.html             marketing landing page (served at /landing)
```

## Setup & run

```bash
cd backend
cp .env.example .env        # then fill in YOUTUBE_API_KEY + OPENROUTER_API_KEY
uv run uvicorn main:app --reload
# or: pip install -r requirements.txt && uvicorn main:app --reload
```

- Search page:   http://localhost:8000/
- Landing page:  http://localhost:8000/landing
- API:           `POST /api/scan`  body `{"niche": "calisthenics"}`
- CLI:           `python run_cli.py calisthenics`

## How the analysis is weighted (Content Mode)

| Signal | Weight | Why |
|---|---|---|
| **Comments** | **3× (highest)** | Real questions/pain — the exact words people use |
| **Titles** | 2× | What angles already exist + creator keywords (free) |
| views / likes | demand proxy | Proven interest (free, from statistics) |
| descriptions | minor | Occasionally reveals subtopics |
| transcripts | skipped | Show what the creator said, not what the audience wants (v2) |

Weighting lives in `backend/app/services/analyzer.py` (`WEIGHTS`).

## Reddit

Reddit unlocks automatically once you add `REDDIT_CLIENT_ID` /
`REDDIT_CLIENT_SECRET` to `backend/.env` — no code changes needed.
