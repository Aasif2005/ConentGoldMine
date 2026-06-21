"""Loads configuration from the .env file."""
import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "content-goldmine/0.1")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

HAS_REDDIT = bool(REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET)
HAS_YOUTUBE = bool(YOUTUBE_API_KEY)
HAS_OPENAI = bool(OPENAI_API_KEY)
