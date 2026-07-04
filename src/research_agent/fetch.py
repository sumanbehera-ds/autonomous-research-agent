from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx
import trafilatura
from bs4 import BeautifulSoup

from research_agent.models import SearchResult, SourceDocument
from research_agent.utils import compact_text


@dataclass
class WebContentFetcher:
    timeout_seconds: int = 20
    max_chars: int = 12000
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    )

    async def fetch_all(self, results: list[SearchResult]) -> list[SourceDocument]:
        timeout = httpx.Timeout(self.timeout_seconds)
        headers = {"User-Agent": self.user_agent}
        async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
            tasks = [self._fetch_one(client, result) for result in results]
            fetched = await asyncio.gather(*tasks, return_exceptions=True)

        documents: list[SourceDocument] = []
        for item in fetched:
            if isinstance(item, SourceDocument) and item.content:
                documents.append(item)
        return documents

    async def _fetch_one(self, client: httpx.AsyncClient, result: SearchResult) -> SourceDocument | None:
        try:
            response = await client.get(result.url)
            response.raise_for_status()
        except Exception:
            return None

        content_type = response.headers.get("content-type", "").lower()
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            return None

        text = extract_readable_text(response.text)
        if not text:
            text = result.snippet
        text = compact_text(text, self.max_chars)
        if len(text) < 200:
            return None

        return SourceDocument(
            title=result.title,
            url=str(response.url),
            content=text,
            query=result.query,
        )


def extract_readable_text(html: str) -> str:
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )
    if extracted:
        return extracted

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "form", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)
