from pathlib import Path

from research_agent.memory import ResearchMemory


def test_memory_saves_and_reads_run(tmp_path: Path):
    memory = ResearchMemory(tmp_path / "memory.sqlite3")
    run_id = memory.save_run(
        topic="Agentic AI",
        plan={"intent": "research", "search_queries": ["agentic ai"], "source_strategy": "web"},
        sources=[{"title": "Source", "url": "https://example.com"}],
        report_path="reports/example.md",
        pdf_path=None,
        report_preview="Preview",
    )

    rows = memory.list_runs()
    assert rows[0]["id"] == run_id

    row = memory.get_run(run_id)
    assert row is not None
    assert row["topic"] == "Agentic AI"
    assert row["plan"]["search_queries"] == ["agentic ai"]
