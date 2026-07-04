from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from research_agent.exporters import ReportExporter
from research_agent.fetch import WebContentFetcher
from research_agent.llm import OpenAIChatClient, OllamaChatClient, create_llm_client
from research_agent.memory import ResearchMemory
from research_agent.models import (
    AnalyzedSource,
    ResearchPlan,
    ResearchResult,
    SearchResult,
    SourceDocument,
)
from research_agent.prompts import (
    ANALYZER_SYSTEM,
    PLANNER_SYSTEM,
    SYNTHESIZER_SYSTEM,
    analyzer_prompt,
    planner_prompt,
    synthesis_prompt,
)
from research_agent.search import SearchProvider, default_search_provider
from research_agent.utils import compact_text, unique_by_url

ProgressCallback = Callable[[str, str], None]


@dataclass
class ResearchAgent:
    llm: OpenAIChatClient | OllamaChatClient
    search_provider: SearchProvider
    fetcher: WebContentFetcher
    exporter: ReportExporter
    memory: ResearchMemory
    on_event: ProgressCallback | None = None

    @classmethod
    def from_environment(
        cls,
        *,
        output_dir: str | Path = "reports",
        memory_db: str | Path = ".agent_memory/research_history.sqlite3",
        on_event: ProgressCallback | None = None,
    ) -> "ResearchAgent":
        return cls(
            llm=create_llm_client(),
            search_provider=default_search_provider(),
            fetcher=WebContentFetcher(),
            exporter=ReportExporter(Path(output_dir)),
            memory=ResearchMemory(Path(memory_db)),
            on_event=on_event,
        )

    def run(
        self,
        topic: str,
        *,
        max_queries: int = 3,
        max_sources: int = 6,
        max_results_per_query: int = 5,
        export_pdf: bool = False,
    ) -> ResearchResult:
        topic = topic.strip()
        if not topic:
            raise ValueError("A research topic is required.")

        self._emit("plan", "Creating autonomous research plan")
        plan = self._create_plan(topic, max_queries=max_queries)

        self._emit("search", f"Searching external sources using {len(plan.search_queries)} queries")
        search_results = self._search(plan.search_queries, max_results_per_query=max_results_per_query)
        if not search_results:
            raise RuntimeError("No search results were found. Try a more specific topic or configure Tavily.")

        self._emit("fetch", f"Fetching and extracting up to {max_sources} useful sources")
        documents = self._fetch(search_results, max_sources=max_sources)
        if not documents:
            raise RuntimeError("Search results were found, but no readable source content could be extracted.")

        self._emit("analyze", "Analyzing relevance and extracting source-backed facts")
        analyzed_sources = self._analyze(topic, documents)
        useful_sources = [
            source for source in analyzed_sources
            if source.relevance_score >= 0.45 and source.key_facts
        ]
        if not useful_sources:
            raise RuntimeError("Sources were fetched, but the LLM did not find enough relevant evidence.")

        self._emit("synthesize", "Synthesizing structured report")
        report = self._synthesize(topic, plan, useful_sources)

        self._emit("export", "Saving report files")
        markdown_path = self.exporter.save_markdown(topic, report)
        pdf_path = self.exporter.save_pdf(markdown_path, report) if export_pdf else None

        self._emit("memory", "Storing run in local memory")
        memory_id = self.memory.save_run(
            topic=topic,
            plan=asdict(plan),
            sources=[asdict(source) for source in useful_sources],
            report_path=str(markdown_path),
            pdf_path=str(pdf_path) if pdf_path else None,
            report_preview=compact_text(report, 700),
        )

        return ResearchResult(
            topic=topic,
            plan=plan,
            markdown_report=report,
            markdown_path=markdown_path,
            pdf_path=pdf_path,
            analyzed_sources=useful_sources,
            raw_sources=documents,
            memory_id=memory_id,
            metadata={
                "searched_results": len(search_results),
                "fetched_sources": len(documents),
            },
        )

    def _create_plan(self, topic: str, *, max_queries: int) -> ResearchPlan:
        data = self.llm.complete_json(
            PLANNER_SYSTEM,
            planner_prompt(topic, max_queries=max_queries),
            temperature=0.2,
        )
        queries = [
            str(query).strip()
            for query in data.get("search_queries", [])
            if str(query).strip()
        ]
        if not queries:
            raise RuntimeError("The LLM did not produce any search queries.")
        return ResearchPlan(
            intent=str(data.get("intent", "")).strip() or topic,
            source_strategy=str(data.get("source_strategy", "")).strip(),
            search_queries=queries[:max_queries],
        )

    def _search(self, queries: list[str], *, max_results_per_query: int) -> list[SearchResult]:
        results: list[SearchResult] = []
        for query in queries:
            try:
                results.extend(self.search_provider.search(query, max_results_per_query))
            except Exception as exc:
                self._emit("search", f"Search failed for query '{query}': {exc}")
        return unique_by_url(results, lambda item: item.url)

    def _fetch(self, results: list[SearchResult], *, max_sources: int) -> list[SourceDocument]:
        candidates = results[: max(max_sources * 2, max_sources)]
        documents = asyncio.run(self.fetcher.fetch_all(candidates))
        return unique_by_url(documents, lambda item: item.url)[:max_sources]

    def _analyze(self, topic: str, documents: list[SourceDocument]) -> list[AnalyzedSource]:
        data = self.llm.complete_json(
            ANALYZER_SYSTEM,
            analyzer_prompt(topic, documents),
            temperature=0.1,
        )
        analyzed: list[AnalyzedSource] = []
        for item in data.get("sources", []):
            facts = [
                str(fact).strip()
                for fact in item.get("key_facts", [])
                if str(fact).strip()
            ]
            try:
                score = float(item.get("relevance_score", 0))
            except (TypeError, ValueError):
                score = 0.0
            analyzed.append(
                AnalyzedSource(
                    title=str(item.get("title", "")).strip(),
                    url=str(item.get("url", "")).strip(),
                    relevance_score=max(0.0, min(1.0, score)),
                    key_facts=facts,
                    discard_reason=item.get("discard_reason"),
                )
            )
        return analyzed

    def _synthesize(self, topic: str, plan: ResearchPlan, sources: list[AnalyzedSource]) -> str:
        payload = []
        for index, source in enumerate(sources, start=1):
            payload.append(
                {
                    "id": f"S{index}",
                    "title": source.title,
                    "url": source.url,
                    "relevance_score": source.relevance_score,
                    "key_facts": source.key_facts,
                }
            )
        return self.llm.complete(
            SYNTHESIZER_SYSTEM,
            synthesis_prompt(topic, plan.intent, plan.source_strategy, payload),
            temperature=0.2,
        )

    def _emit(self, stage: str, message: str) -> None:
        if self.on_event:
            self.on_event(stage, message)
