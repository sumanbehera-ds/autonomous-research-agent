from pathlib import Path

from research_agent.exporters import ReportExporter
from research_agent.memory import ResearchMemory
from research_agent.models import SearchResult, SourceDocument
from research_agent.pipeline import ResearchAgent


class FakeLLM:
    def complete_json(self, system_prompt, user_prompt, *, temperature=None):
        if "planning" in system_prompt:
            return {
                "intent": "Research agentic AI trends.",
                "source_strategy": "Search recent web sources.",
                "search_queries": ["agentic AI trends"],
            }
        return {
            "sources": [
                {
                    "id": "S1",
                    "title": "Example Source",
                    "url": "https://example.com/agentic-ai",
                    "relevance_score": 0.91,
                    "key_facts": ["Agentic AI systems can plan and execute multi-step tasks."],
                    "discard_reason": None,
                }
            ],
            "duplicate_or_overlapping_points": [],
        }

    def complete(self, system_prompt, user_prompt, *, temperature=None, json_mode=False):
        return """# Agentic AI

## Executive Summary
- Agentic AI systems can plan and execute multi-step tasks. [S1]

## Key Points
- Planning and tool use are central capabilities. [S1]

## Important Findings
- The evidence supports building autonomous workflows. [S1]

## Actionable Insights
- Start with a narrow workflow and clear source citations. [S1]

## Limitations
- This is a test run with one source.

## Sources
- [S1] Example Source - https://example.com/agentic-ai
"""


class FakeSearchProvider:
    def search(self, query: str, max_results: int):
        return [
            SearchResult(
                title="Example Source",
                url="https://example.com/agentic-ai",
                snippet="Agentic AI systems can plan.",
                query=query,
            )
        ]


class FakeFetcher:
    async def fetch_all(self, results):
        return [
            SourceDocument(
                title=results[0].title,
                url=results[0].url,
                content="Agentic AI systems can plan and execute multi-step tasks.",
                query=results[0].query,
            )
        ]


def test_pipeline_creates_report_and_memory(tmp_path: Path):
    agent = ResearchAgent(
        llm=FakeLLM(),
        search_provider=FakeSearchProvider(),
        fetcher=FakeFetcher(),
        exporter=ReportExporter(tmp_path / "reports"),
        memory=ResearchMemory(tmp_path / "memory.sqlite3"),
    )

    result = agent.run("Agentic AI", max_queries=1, max_sources=1)

    assert result.markdown_path.exists()
    assert result.memory_id == 1
    assert result.analyzed_sources[0].url == "https://example.com/agentic-ai"
