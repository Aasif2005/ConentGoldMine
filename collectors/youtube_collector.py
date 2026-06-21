"""Collect public YouTube data for a niche: video titles, stats, and comments.

Why these fields:
- title/description -> what topics already exist + keywords creators use
- viewCount/likeCount -> a demand proxy (proven interest)
- top comments      -> the richest pain/feedback signal (real questions)
Transcripts are intentionally skipped (heavy, and they show what the creator
said, not what the audience wants).
"""
from __future__ import annotations
import config


def _to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def collect_youtube(niche: str, max_videos: int = 10) -> dict:
    """Return {'items': [...], 'videos': [...]}. Empty if no API key."""
    if not config.HAS_YOUTUBE:
        print("[youtube] No API key - skipping. Set YOUTUBE_API_KEY in .env")
        return {"items": [], "videos": []}

    from googleapiclient.discovery import build

    yt = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
    items: list[dict] = []
    videos: list[dict] = []

    # 1) Search for relevant videos -> collect their IDs
    try:
        search = yt.search().list(
            q=niche, part="snippet", type="video",
            maxResults=max_videos, relevanceLanguage="en",
        ).execute()
    except Exception as e:
        print(f"[youtube] search failed: {e}")
        return {"items": [], "videos": []}

    video_ids = [v["id"]["videoId"] for v in search.get("items", []) if v.get("id", {}).get("videoId")]
    if not video_ids:
        return {"items": [], "videos": []}

    # 2) One batched call to get titles, descriptions AND statistics (free-ish, 1 call)
    stats_by_id: dict[str, dict] = {}
    try:
        details = yt.videos().list(
            part="snippet,statistics", id=",".join(video_ids),
        ).execute()
        for d in details.get("items", []):
            sn = d.get("snippet", {})
            st = d.get("statistics", {})
            stats_by_id[d["id"]] = {
                "title": sn.get("title", ""),
                "description": sn.get("description", ""),
                "channel": sn.get("channelTitle", ""),
                "views": _to_int(st.get("viewCount")),
                "likes": _to_int(st.get("likeCount")),
                "comment_count": _to_int(st.get("commentCount")),
            }
    except Exception as e:
        print(f"[youtube] video details failed: {e}")

    # 3) Build items (one per video) + pull top comments per video
    for vid in video_ids:
        meta = stats_by_id.get(vid, {})
        title = meta.get("title", "")
        views = meta.get("views", 0)
        likes = meta.get("likes", 0)
        video_url = "https://youtube.com/watch?v=" + vid

        videos.append({
            "title": title,
            "url": video_url,
            "channel": meta.get("channel", ""),
            "views": views,
            "likes": likes,
            "comment_count": meta.get("comment_count", 0),
        })

        items.append({
            "source": "youtube",
            "kind": "video_title",
            "text": f"{title}. {meta.get('description', '')[:300]}",
            "score": views,          # use view count as the demand proxy for titles
            "likes": likes,
            "views": views,
            "url": video_url,
            "community": "YouTube",
        })

        # Top comments are where the real questions/feedback live
        try:
            ct = yt.commentThreads().list(
                part="snippet", videoId=vid, maxResults=20,
                order="relevance", textFormat="plainText",
            ).execute()
            for c in ct.get("items", []):
                top = c["snippet"]["topLevelComment"]["snippet"]
                txt = top.get("textDisplay", "")
                if len(txt) > 40:
                    items.append({
                        "source": "youtube",
                        "kind": "comment",
                        "text": txt[:500],
                        "score": _to_int(top.get("likeCount")),
                        "url": video_url,
                        "community": "YouTube",
                    })
        except Exception as e:
            print(f"[youtube] comments disabled/failed for {vid}: {e}")

    print(f"[youtube] collected {len(items)} items across {len(videos)} videos")
    return {"items": items, "videos": videos}
