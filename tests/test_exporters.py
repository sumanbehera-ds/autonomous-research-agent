from pathlib import Path

from research_agent.exporters import ReportExporter


def test_add_author_profile_inserts_details_after_title(tmp_path: Path):
    exporter = ReportExporter(
        tmp_path / "reports",
        author_name="Suman Behera",
        author_linkedin="https://www.linkedin.com/in/suman-behera",
        author_portfolio="https://github.com/sumanbehera-ds",
    )

    report = exporter.add_author_profile("# Topic\n\n## Executive Summary\nContent")

    assert report.startswith(
        "# Topic\n\n"
        "Author: Suman Behera\n"
        "LinkedIn: https://www.linkedin.com/in/suman-behera\n"
        "Portfolio: https://github.com/sumanbehera-ds"
    )
