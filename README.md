# Autonomous Research Agent

An autonomous AI research agent that accepts a user topic, creates a research plan, searches external sources, extracts relevant information, filters duplicate or irrelevant content, generates a structured research report, and stores previous research runs in local memory.

This project was built for **Assessment Option 1: Autonomous Research Agent**.

---

## Author

**Suman Behera**

- Portfolio: https://sumanbehera-ds.github.io/Suman-Portfolio/
- LinkedIn: https://www.linkedin.com/in/suman-01-behera/
- GitHub: https://github.com/sumanbehera-ds

---

## Problem Statement

The objective is to build an autonomous AI agent that can collect information from external sources, analyze the collected content, and generate a structured, actionable summary with references.

The agent should not rely on hardcoded answers or predefined static outputs. It should use an LLM to reason over the user query, plan research steps, evaluate source content, and generate the final report.

---

## What This Agent Does

The agent accepts a research topic and autonomously performs the following steps:

1. Understands the user's research goal using an LLM.
2. Creates a research plan and search queries.
3. Searches external sources.
4. Fetches and extracts readable webpage content.
5. Removes repeated URLs and duplicate source content.
6. Filters irrelevant or low-value information.
7. Uses the LLM to analyze the extracted evidence.
8. Generates a structured report with:
   - Key points
   - Important findings
   - References / sources
   - Actionable insights
   - Limitations
9. Exports the report as Markdown.
10. Optionally exports the report as PDF.
11. Stores previous research runs in local SQLite memory.

---

## Key Features

- LLM-based autonomous research planning
- External web search
- Webpage content extraction
- Duplicate source removal
- Relevance filtering
- Source-backed summarization
- Markdown report export
- Optional PDF report export
- SQLite-based local memory
- CLI interface
- Test coverage with Pytest
- Supports local Ollama or OpenAI-compatible LLM APIs

---

## Architecture

```text
User Topic
   ↓
LLM Research Planner
   ↓
Search Query Generation
   ↓
External Web Search
   ↓
Webpage Fetching and Text Extraction
   ↓
Duplicate and Relevance Filtering
   ↓
LLM Evidence Analysis
   ↓
Structured Report Generation
   ↓
Markdown / PDF Export
   ↓
SQLite Memory Storage
```

---

## Project Structure

```text
autonomous-research-agent/
│
├── src/
│   └── research_agent/
│       ├── cli.py          # Command-line interface
│       ├── pipeline.py     # End-to-end autonomous workflow
│       ├── llm.py          # LLM client setup
│       ├── prompts.py      # Planner, analyzer, and synthesis prompts
│       ├── search.py       # Web search providers
│       ├── fetch.py        # Webpage fetching and text extraction
│       ├── memory.py       # SQLite memory storage
│       ├── exporters.py    # Markdown and PDF export
│       ├── models.py       # Shared data models
│       └── utils.py        # Utility functions
│
├── tests/
│   ├── test_exporters.py
│   ├── test_memory.py
│   ├── test_pipeline.py
│   └── test_utils.py
│
├── examples/
│   ├── sample_report.md
│   └── sample_report.pdf
│
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── requirements.txt
```

---

## Tech Stack

- Python 3.10+
- OpenAI-compatible LLM API
- Ollama local LLM support
- HTTPX
- BeautifulSoup
- Trafilatura
- SQLite
- ReportLab
- Pytest

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/sumanbehera-ds/autonomous-research-agent.git
cd autonomous-research-agent
```

### 2. Create Virtual Environment

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

For macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

---

## Environment Configuration

Copy the example environment file:

For Windows:

```powershell
copy .env.example .env
```

For macOS/Linux:

```bash
cp .env.example .env
```

---

## LLM Configuration

The project supports two execution modes.

---

### Option A: Use Local Ollama

This option runs with a local model and does not require an OpenAI API key.

Example `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434

AUTHOR_NAME=Suman Behera
AUTHOR_PORTFOLIO=https://sumanbehera-ds.github.io/Suman-Portfolio/
AUTHOR_LINKEDIN=https://www.linkedin.com/in/suman-01-behera/
```

Install Ollama and pull a model:

```bash
ollama pull llama3.1
```

Keep Ollama running while using the agent.

---

### Option B: Use OpenAI or OpenAI-Compatible API

Example `.env`:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini

AUTHOR_NAME=Suman Behera
AUTHOR_PORTFOLIO=https://sumanbehera-ds.github.io/Suman-Portfolio/
AUTHOR_LINKEDIN=https://www.linkedin.com/in/suman-01-behera/
```

Optional search API:

```env
TAVILY_API_KEY=your_tavily_api_key_here
```

If `TAVILY_API_KEY` is not provided, the agent falls back to DuckDuckGo-based search.

---

## Usage

Run a research task:

```bash
research-agent run "Latest trends in agentic AI for cybersecurity"
```

Short form:

```bash
research-agent "Latest trends in agentic AI for cybersecurity"
```

Generate both Markdown and PDF reports:

```bash
research-agent run "AI automation in security operations" --pdf
```

Limit the number of sources:

```bash
research-agent run "Open source LLM observability tools" --max-sources 5
```

Control search depth:

```bash
research-agent run "AI agents for vulnerability management" --max-queries 3 --max-results-per-query 5
```

---

## View Previous Research Runs

Show previous runs stored in local memory:

```bash
research-agent history
```

Show details for one saved run:

```bash
research-agent show 1
```

---

## Output

Generated reports are saved in the `reports/` folder.

Example output:

```text
Research complete.
Memory ID: 3
Markdown: reports/20260704-144134-ai-automation-in-security-operations.md
PDF: reports/20260704-144134-ai-automation-in-security-operations.pdf
Sources used: 3
```

Local memory is stored at:

```text
.agent_memory/research_history.sqlite3
```

The memory database is intentionally ignored by Git because it is runtime-generated local data.

---

## Sample Output

A sample generated report is available in the `examples/` folder:

```text
examples/sample_report.md
examples/sample_report.pdf
```

The sample report demonstrates the agent's ability to search, extract, analyze, summarize, cite sources, and export the final result.

---

## Run Tests

```bash
pytest
```

Expected result:

```text
6 passed
```

---

## Why This Is Autonomous

This project does not return predefined answers.

The agent uses an LLM to:

- Understand the user's topic
- Generate research queries
- Decide what information is relevant
- Analyze extracted source content
- Remove weak or irrelevant findings
- Generate a structured final report

The final answer changes based on the user's topic and the live information collected from external sources.

---

## Assessment Requirement Coverage

| Requirement | Status |
|---|---|
| Accept user query/topic | Completed |
| Search external sources | Completed |
| Extract relevant information | Completed |
| Remove duplicate or irrelevant content | Completed |
| Generate structured summary | Completed |
| Include key points | Completed |
| Include important findings | Completed |
| Include references/sources | Completed |
| Include actionable insights | Completed |
| Export Markdown | Completed |
| Export PDF | Completed |
| Store previous searches in memory | Completed |

---

## Limitations

- Search quality depends on external search availability.
- Some websites may block automated fetching.
- LLM output quality depends on the configured model.
- The agent stores local memory only; no cloud database is used.
- The system is designed for research assistance, not final expert decision-making.

---

## Reviewer Notes

- The project is implemented as an original Python package.
- The agent performs real external search and webpage extraction.
- The final report is generated dynamically by an LLM.
- The code includes tests for core functionality.
- The project can run with either a local Ollama model or an OpenAI-compatible API.

---

## License

This project is submitted as an assessment solution by Suman Behera.
