from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

import httpx
from bs4 import BeautifulSoup

from research_agent.models import SearchResult
from research_agent.utils import normalize_url, unique_by_url


class SearchProvider(Protocol):
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        ...


@dataclass
class TavilySearchProvider:
    api_key: str | None = None

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is required for TavilySearchProvider.")

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        }
        with httpx.Client(timeout=20) as client:
            response = client.post("https://api.tavily.com/search", json=payload)
            response.raise_for_status()
            data = response.json()

        results = []
        for item in data.get("results", []):
            url = item.get("url")
            if not url:
                continue
            results.append(
                SearchResult(
                    title=item.get("title") or url,
                    url=normalize_url(url),
                    snippet=item.get("content") or "",
                    query=query,
                )
            )
        return unique_by_url(results, lambda result: result.url)[:max_results]


@dataclass
class DuckDuckGoSearchProvider:
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    )

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        headers = {"User-Agent": self.user_agent}
        with httpx.Client(headers=headers, timeout=20, follow_redirects=True) as client:
            response = client.get("https://duckduckgo.com/html/", params={"q": query})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SearchResult] = []

        for result in soup.select(".result"):
            link = result.select_one("a.result__a")
            if not link:
                continue
            url = link.get("href") or ""
            if not url:
                continue
            snippet_node = result.select_one(".result__snippet")
            results.append(
                SearchResult(
                    title=link.get_text(" ", strip=True),
                    url=normalize_url(url),
                    snippet=snippet_node.get_text(" ", strip=True) if snippet_node else "",
                    query=query,
                )
            )
            if len(results) >= max_results:
                break

        return unique_by_url(results, lambda item: item.url)[:max_results]


def default_search_provider() -> SearchProvider:
    if os.getenv("TAVILY_API_KEY"):
        return TavilySearchProvider()
    return DuckDuckGoSearchProvider()
