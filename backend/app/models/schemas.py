"""Model layer: pydantic schemas for the request and the scan report.

These are the API contract. The route uses ScanReport as its response_model so
FastAPI validates and documents every response automatically.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    niche: str


class Topic(BaseModel):
    title: str = ""
    demand: int = 0
    format: str = "Video"
    example_quote: str = ""


class Video(BaseModel):
    title: str = ""
    url: str = ""
    channel: str = ""
    views: int = 0
    likes: int = 0
    comment_count: int = 0
    description: str = ""


class Community(BaseModel):
    name: str = ""
    subscribers: int = 0
    mentions: int = 0


class ScanStats(BaseModel):
    scanned: int = 0
    topics: int = 0
    communities: int = 0
    videos: int = 0
    comments: int = 0
    titles: int = 0


class ScanReport(BaseModel):
    niche: str
    stats: ScanStats = Field(default_factory=ScanStats)
    topics: List[Topic] = Field(default_factory=list)
    videos: List[Video] = Field(default_factory=list)
    communities: List[Community] = Field(default_factory=list)
    cached: bool = False
    error: Optional[str] = None
