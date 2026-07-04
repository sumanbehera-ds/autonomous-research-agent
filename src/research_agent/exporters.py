from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from research_agent.utils import ensure_directory, slugify


@dataclass
class ReportExporter:
    output_dir: Path = Path("reports")

    def __post_init__(self) -> None:
        ensure_directory(self.output_dir)

    def save_markdown(self, topic: str, markdown: str) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        path = self.output_dir / f"{stamp}-{slugify(topic)}.md"
        path.write_text(markdown.strip() + "\n", encoding="utf-8")
        return path

    def save_pdf(self, markdown_path: Path, markdown: str) -> Path:
        pdf_path = markdown_path.with_suffix(".pdf")
        render_markdown_to_pdf(markdown, pdf_path)
        return pdf_path


def render_markdown_to_pdf(markdown: str, pdf_path: Path) -> None:
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=LETTER,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    story = []
    bullet_items = []

    def flush_bullets() -> None:
        nonlocal bullet_items
        if bullet_items:
            story.append(ListFlowable(bullet_items, bulletType="bullet", leftIndent=18))
            story.append(Spacer(1, 8))
            bullet_items = []

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            flush_bullets()
            story.append(Spacer(1, 6))
            continue

        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(_escape(line[2:]), styles["Title"]))
            story.append(Spacer(1, 12))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(_escape(line[3:]), styles["Heading2"]))
            story.append(Spacer(1, 6))
        elif line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(_escape(line[4:]), styles["Heading3"]))
            story.append(Spacer(1, 4))
        elif line.startswith("- "):
            bullet_items.append(ListItem(Paragraph(_escape(line[2:]), styles["BodyText"])))
        else:
            flush_bullets()
            story.append(Paragraph(_escape(line), styles["BodyText"]))
            story.append(Spacer(1, 6))

    flush_bullets()
    doc.build(story)


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
