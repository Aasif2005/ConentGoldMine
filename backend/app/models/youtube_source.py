"""Model layer: public YouTube data source for a niche.

Content Mode data priority (most -> least useful):
  COMMENTS    -> richest pain/demand signal (real questions & complaints)
  TITLES      -> what angles already exist + the keywords creators use (free)
  views/likes -> demand proxy (free, comes with statistics)
  descriptions-> minor; occasionally reveals subtopics
Transcripts are intentionally skipped (they show what the creator said, not
what the audience wants, and are expensive/fragile to fetch).
"""
from __future__ import annotations
from app.models import config


def _to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


class YouTubeSource:
    """Collects titles + statistics + top comments for a niche."""

    def collect(self, niche: str, max_videos: int = 10) -> dict:
        """Return {'items': [...], 'videos': [...]}. Empty if no API key."""
        if not config.HAS_YOUTUBE:
            print("[youtube] No API key - skipping. Set YOUTUBE_API_KEY in .env")
            return {"items": [], "videos": []}

        from googleapiclient.discovery import build

        yt = build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)
        items: list[dict] = []
        videos: list[dict] = []

        # 1) Search for relevant videos -> collect their IDs (titles come free here)
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

        # 2) One batched call for titles, descriptions AND statistics (free demand proxy)
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

        # 3) Build one title item per video + pull top comments (the real pain signal)
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
                "description": meta.get("description", "")[:280],
            })

            items.append({
                "source": "youtube",
                "kind": "video_title",
                "text": f"{title}. {meta.get('description', '')[:300]}",
                "score": views,
                "likes": likes,
                "views": views,
                "url": video_url,
                "community": "YouTube",
            })

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
