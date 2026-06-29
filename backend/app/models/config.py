"""Model layer: configuration loaded from the .env file."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Reddit API ---
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "content-goldmine/0.1")

# --- YouTube Data API v3 ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# --- LLM provider: OpenRouter (preferred) or OpenAI ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "ContentGoldmine")

# OpenAI is used only if OPENROUTER_API_KEY is empty.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

HAS_REDDIT = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)
HAS_YOUTUBE = bool(YOUTUBE_API_KEY)
HAS_OPENROUTER = bool(OPENROUTER_API_KEY)
HAS_OPENAI = bool(OPENAI_API_KEY)
HAS_LLM = HAS_OPENROUTER or HAS_OPENAI
