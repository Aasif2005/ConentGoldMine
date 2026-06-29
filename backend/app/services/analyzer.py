"""Service layer: turn raw items into ranked content topics.

Weighting (per the Content Mode data priority):
  COMMENTS  -> weighted HIGHEST (real audience pain / questions)
  TITLES    -> weighted second  (existing angles + creator keywords)
  views/likes ride along as a demand proxy; transcripts are skipped.

Uses an LLM (OpenRouter preferred, else OpenAI) when a key is set; otherwise a
free keyword-frequency fallback so the MVP always returns output.
"""
from __future__ import annotations
import collections
import json
import re
from app.models import config

# How strongly each source type counts toward demand.
WEIGHTS = {"comment": 3, "post": 2, "video_title": 2}


def _weight(item: dict) -> int:
    return WEIGHTS.get(item.get("kind", ""), 1)


_LABELS = {"comment": "COMMENT", "video_title": "TITLE", "post": "POST"}

PROMPT_TEMPLATE = (
    'You are a content strategist. Below are real public posts/comments from '
    'people in the "<NICHE>" niche.\n'
    'Each line is tagged by source: [COMMENT] = an audience question or pain '
    '(WEIGHT THESE HIGHEST), [TITLE] = an existing video angle, [POST] = a '
    'forum post.\n'
    'Cluster them into 5-8 distinct TOPICS people most want content about, '
    'weighting COMMENTS highest, then TITLES.\n'
    'For each topic return:\n'
    '- title: the question or pain in plain words\n'
    '- demand: a 1-100 score based on how often AND how intensely it appears\n'
    "- format: best content format (e.g. 'YouTube video', 'Reel/Short', 'Carousel', 'Blog')\n"
    '- example_quote: one short representative quote, lightly trimmed\n\n'
    'Return ONLY valid JSON (no markdown, no commentary) in exactly this shape:\n'
    '{"topics": [{"title": "...", "demand": 80, "format": "Reel/Short", "example_quote": "..."}]}\n\n'
    'POSTS:\n<POSTS>\n'
)


class Analyzer:
    def analyze(self, niche: str, items: list[dict]) -> list[dict]:
        if not items:
            return []
        # Highest-signal items (comments) first.
        ordered = sorted(items, key=_weight, reverse=True)
        if not any(it.get("text") for it in ordered):
            return []
        if config.HAS_LLM:
            try:
                return self._llm_cluster(niche, ordered)
            except Exception as e:
                print(f"[analyzer] LLM failed ({e}); using keyword fallback")
        return self._keyword_cluster(ordered)

    # --- LLM path -----------------------------------------------------------
    def _llm_cluster(self, niche: str, ordered: list[dict]) -> list[dict]:
        from openai import OpenAI

        lines = []
        for it in ordered[:120]:
            t = it.get("text")
            if not t:
                continue
            tag = _LABELS.get(it.get("kind", ""), "TEXT")
            lines.append(f"- [{tag}] {t}")
        sample = "\n".join(lines)
        prompt = PROMPT_TEMPLATE.replace("<NICHE>", niche).replace("<POSTS>", sample)

        if config.HAS_OPENROUTER:
            client = OpenAI(api_key=config.OPENROUTER_API_KEY, base_url=config.OPENROUTER_BASE_URL)
            model = config.OPENROUTER_MODEL
            extra_headers = {}
            if config.OPENROUTER_SITE_URL:
                extra_headers["HTTP-Referer"] = config.OPENROUTER_SITE_URL
            if config.OPENROUTER_APP_NAME:
                extra_headers["X-Title"] = config.OPENROUTER_APP_NAME
            provider = "openrouter"
        else:
            client = OpenAI(api_key=config.OPENAI_API_KEY)
            model = config.OPENAI_MODEL
            extra_headers = {}
            provider = "openai"

        print(f"[analyzer] using {provider} model={model}")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000,
            extra_headers=extra_headers or None,
        )
        content = resp.choices[0].message.content or ""
        data = self._extract_json(content)
        topics = data.get("topics", []) if isinstance(data, dict) else []

        cleaned = []
        for t in topics:
            if not isinstance(t, dict):
                continue
            try:
                t["demand"] = int(t.get("demand", 0))
            except (TypeError, ValueError):
                t["demand"] = 0
            cleaned.append(t)
        cleaned.sort(key=lambda t: t.get("demand", 0), reverse=True)
        return cleaned

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Robustly pull a JSON object out of a (possibly reasoning) model reply."""
        text = (text or "").strip()
        fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    # --- Free fallback ------------------------------------------------------
    def _keyword_cluster(self, ordered: list[dict]) -> list[dict]:
        words: collections.Counter = collections.Counter()
        example_for: dict[str, str] = {}
        for it in ordered:
            t = it.get("text", "")
            if not t:
                continue
            mult = _weight(it)  # comments count 3x, titles/posts 2x
            for w in re.findall(r"[a-zA-Z]{4,}", t.lower()):
                if w not in STOP:
                    words[w] += mult
                    example_for.setdefault(w, t)
        top = words.most_common(8)
        if not top:
            return []
        maxc = top[0][1]
        topics = []
        for w, c in top:
            topics.append({
                "title": f"Content about '{w}'",
                "demand": int(100 * c / maxc),
                "format": "Reel/Short",
                "example_quote": (example_for.get(w, "") or "")[:200],
            })
        return topics


STOP = set(
    "the a an and or but for to of in on with my me i you is are was were not be how do "
    "does what why when where can cant cannot your it this that have has had will would "
    "about just like get got there their they them then than out into more most some any "
    "really very much many also even still here over only your yours from your video".split()
)
