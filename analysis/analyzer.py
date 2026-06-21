"""Turn raw items into ranked topics.

Uses an LLM if OPENAI_API_KEY is set; otherwise falls back to a free
keyword-frequency clustering so the MVP always produces output.
"""
from __future__ import annotations
import json
import re
import collections
import config

# Note: uses .replace() (not .format()) so JSON braces stay readable.
PROMPT_TEMPLATE = (
    'You are a content strategist. Below are real public posts/comments from '
    'people in the "<NICHE>" niche.\n'
    'Cluster them into 5-8 distinct TOPICS that people most want content about.\n'
    'For each topic return:\n'
    '- title: the question or pain in plain words\n'
    '- demand: 1-100, based on how often AND how intensely it appears\n'
    "- format: best content format (e.g. 'YouTube video', 'Reel/Short', 'Carousel', 'Blog')\n"
    '- example_quote: one representative quote, lightly trimmed\n\n'
    'Return ONLY valid JSON in exactly this shape:\n'
    '{"topics": [{"title": "...", "demand": 80, "format": "Reel/Short", "example_quote": "..."}]}\n\n'
    'POSTS:\n<POSTS>\n'
)


def analyze(niche: str, items: list[dict]) -> list[dict]:
    texts = [it["text"] for it in items if it.get("text")]
    if not texts:
        return []
    if config.HAS_OPENAI:
        try:
            return _llm_cluster(niche, texts)
        except Exception as e:
            print(f"[analyzer] LLM failed ({e}); using keyword fallback")
    return _keyword_cluster(texts)


def _llm_cluster(niche: str, texts: list[str]) -> list[dict]:
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    sample = "\n".join(f"- {t}" for t in texts[:120])
    prompt = PROMPT_TEMPLATE.replace("<NICHE>", niche).replace("<POSTS>", sample)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    topics = data.get("topics", [])
    topics.sort(key=lambda t: t.get("demand", 0), reverse=True)
    return topics


STOP = set(
    "the a an and or but for to of in on with my me i you is are was were not be how do "
    "does what why when where can cant cannot your it this that have has had will would "
    "about just like get got there their they them then than out into more most some any".split()
)


def _keyword_cluster(texts: list[str]) -> list[dict]:
    """Crude but free: rank by keyword frequency, build pseudo-topics."""
    words: collections.Counter = collections.Counter()
    for t in texts:
        for w in re.findall(r"[a-zA-Z]{4,}", t.lower()):
            if w not in STOP:
                words[w] += 1
    top = words.most_common(8)
    if not top:
        return []
    maxc = top[0][1]
    topics = []
    for w, c in top:
        example = next((t for t in texts if w in t.lower()), "")
        topics.append({
            "title": f"Content about '{w}'",
            "demand": int(100 * c / maxc),
            "format": "Reel/Short",
            "example_quote": example[:200],
        })
    return topics
