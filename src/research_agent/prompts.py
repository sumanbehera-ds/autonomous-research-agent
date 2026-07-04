from __future__ import annotations

import json

from research_agent.models import SourceDocument
from research_agent.utils import compact_text


PLANNER_SYSTEM = """You are an autonomous research planning agent.
Your job is to understand the user's research goal, decide what external information is needed, and create useful search queries.
Return only valid JSON."""


def planner_prompt(topic: str, max_queries: int) -> str:
    return f"""Research topic:
{topic}

Create a concise autonomous research plan.

Return JSON with this exact shape:
{{
  "intent": "one sentence explaining the research goal",
  "source_strategy": "what kinds of sources should be searched and why",
  "search_queries": ["query 1", "query 2"]
}}

Rules:
- Generate {max_queries} focused search queries.
- Do not use generic filler queries.
- Prefer queries likely to find recent, factual, source-backed information.
- The queries must be based on the user's topic, not predefined examples."""


ANALYZER_SYSTEM = """You are an evidence extraction agent.
You evaluate web source text against the user's research topic.
Extract only useful, source-grounded facts.
Return only valid JSON."""


def analyzer_prompt(topic: str, sources: list[SourceDocument], max_chars_per_source: int = 3500) -> str:
    source_payload = []
    for index, source in enumerate(sources, start=1):
        source_payload.append(
            {
                "id": f"S{index}",
                "title": source.title,
                "url": source.url,
                "query": source.query,
                "content": compact_text(source.content, max_chars_per_source),
            }
        )

    return f"""Research topic:
{topic}

Sources:
{json.dumps(source_payload, ensure_ascii=False, indent=2)}

Analyze each source for relevance and factual usefulness.

Return JSON with this exact shape:
{{
  "sources": [
    {{
      "id": "S1",
      "title": "source title",
      "url": "https://example.com",
      "relevance_score": 0.0,
      "key_facts": ["fact from this source"],
      "discard_reason": null
    }}
  ],
  "duplicate_or_overlapping_points": ["repeated point across sources, if any"]
}}

Rules:
- relevance_score must be between 0 and 1.
- Use key_facts only when the fact is supported by the source text.
- If a source is weak or unrelated, use a low score, empty key_facts, and explain discard_reason.
- Remove repeated facts across sources where possible."""


SYNTHESIZER_SYSTEM = """You are an autonomous research synthesis agent.
Use only the provided source evidence.
Write a structured, actionable research report in Markdown.
Do not invent facts.
Every factual bullet should cite source IDs like [S1] or [S2]."""


def synthesis_prompt(topic: str, intent: str, source_strategy: str, analyzed_sources: list[dict]) -> str:
    return f"""Research topic:
{topic}

Research intent:
{intent}

Source strategy:
{source_strategy}

Analyzed source evidence:
{json.dumps(analyzed_sources, ensure_ascii=False, indent=2)}

Write a Markdown report with exactly these sections:

# {topic}

## Executive Summary

## Key Points

## Important Findings

## Actionable Insights

## Limitations

## Sources

Rules:
- Use concise, professional language.
- Cite factual claims with source IDs, for example [S1].
- Include source title and URL in the Sources section.
- If evidence is limited, say so in Limitations.
- Do not mention that you are an AI model."""
