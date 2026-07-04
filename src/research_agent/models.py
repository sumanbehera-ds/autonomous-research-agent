from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    query: str


@dataclass(frozen=True)
class SourceDocument:
    title: str
    url: str
    content: str
    query: str


@dataclass(frozen=True)
class ResearchPlan:
    intent: str
    search_queries: list[str]
    source_strategy: str


@dataclass(frozen=True)
class AnalyzedSource:
    title: str
    url: str
    relevance_score: float
    key_facts: list[str] = field(default_factory=list)
    discard_reason: str | None = None


@dataclass(frozen=True)
class ResearchResult:
    topic: str
    plan: ResearchPlan
    markdown_report: str
    markdown_path: Path
    pdf_path: Path | None
    analyzed_sources: list[AnalyzedSource]
    raw_sources: list[SourceDocument]
    memory_id: int
    metadata: dict[str, Any] = field(default_factory=dict)
