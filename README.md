# Autonomous Research Agent

An autonomous AI research agent for **Assessment Option 1**.

The agent accepts a research topic, creates an LLM-driven research plan,
searches external sources, extracts useful content, removes duplicate or
irrelevant information, and generates a structured report with sources and
actionable insights.

## Author

**Suman Behera**

- Portfolio: https://sumanbehera-ds.github.io/Suman-Portfolio/
- LinkedIn: https://www.linkedin.com/in/suman-01-behera/
- GitHub: https://github.com/sumanbehera-ds

## Problem Statement

Build an autonomous AI agent capable of collecting information from external
sources, analyzing the collected content, and generating a structured,
actionable summary.

The solution should not use hardcoded answers or static responses. It should
use an LLM to reason over the user's topic, decide what to search, evaluate
source content, and generate the final report dynamically.

## What The Agent Does

The agent performs the following workflow:

1. Accepts a user research query or topic.
2. Uses an LLM to understand the goal.
3. Creates a research plan and search queries.
4. Searches external sources.
5. Fetches and extracts readable web content.
6. Removes duplicate URLs and repeated source content.
7. Filters irrelevant or low-value information.
8. Uses the LLM to analyze the extracted evidence.
9. Generates a structured report with key points, findings, sources, and
   actionable insights.
10. Exports the report as Markdown and optionally as PDF.
11. Stores previous research runs in local SQLite memory.

## Key Features

- Autonomous LLM-based research planning
- External web search
- Webpage fetching and content extraction
- Duplicate source removal
- Relevance filtering
- Source-backed report generation
- Markdown export
- Optional PDF export
- SQLite memory for previous runs
- Command-line interface
- Pytest test coverage
- Supports local Ollama or OpenAI-compatible LLM APIs

## Architecture

```text
User Topic
  -> LLM Research Planner
  -> Search Query Generation
  -> External Web Search
  -> Webpage Fetching and Text Extraction
  -> Duplicate and Relevance Filtering
  -> LLM Evidence Analysis
  -> Structured Report Generation
  -> Markdown / PDF Export
  -> SQLite Memory Storage
```

## Project Structure

```text
autonomous-research-agent/
|-- src/
|   `-- research_agent/
|       |-- cli.py
|       |-- pipeline.py
|       |-- llm.py
|       |-- prompts.py
|       |-- search.py
|       |-- fetch.py
|       |-- memory.py
|       |-- exporters.py
|       |-- models.py
|       `-- utils.py
|
|-- tests/
|   |-- test_exporters.py
|   |-- test_memory.py
|   |-- test_pipeline.py
|   `-- test_utils.py
|
|-- examples/
|   |-- sample_report.md
|   `-- sample_report.pdf
|
|-- .env.example
|-- .gitignore
|-- README.md
|-- pyproject.toml
`-- requirements.txt
```

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

## Installation

### 1. Clone The Repository

```bash
git clone https://github.com/sumanbehera-ds/autonomous-research-agent.git
cd autonomous-research-agent
```

### 2. Create A Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

## Environment Configuration

Copy the example environment file.

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

## LLM Configuration

The project supports two execution modes.

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

### Option B: Use OpenAI Or OpenAI-Compatible API

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

If `TAVILY_API_KEY` is not provided, the agent falls back to DuckDuckGo-based
search.

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

## View Previous Research Runs

Show previous runs stored in local memory:

```bash
research-agent history
```

Show details for one saved run:

```bash
research-agent show 1
```

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

The memory database is ignored by Git because it is runtime-generated local
data.

## Sample Output

A sample generated report is available in the `examples/` folder:

```text
examples/sample_report.md
examples/sample_report.pdf
```

The sample report demonstrates that the agent can search, extract, analyze,
summarize, cite sources, and export the final result.

## Run Tests

```bash
pytest
```

Expected result:

```text
6 passed
```

## Why This Is Autonomous

This project does not return predefined answers.

The agent uses an LLM to:

- Understand the user's topic
- Generate research queries
- Decide what information is relevant
- Analyze extracted source content
- Remove weak or irrelevant findings
- Generate a structured final report

The final answer changes based on the user's topic and the live information
collected from external sources.

## Assessment Requirement Coverage

| Requirement | Status |
| --- | --- |
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

## Limitations

- Search quality depends on external search availability.
- Some websites may block automated fetching.
- LLM output quality depends on the configured model.
- The agent stores local memory only; no cloud database is used.
- The system is designed for research assistance, not final expert
  decision-making.

## Reviewer Notes

- The project is implemented as an original Python package.
- The agent performs real external search and webpage extraction.
- The final report is generated dynamically by an LLM.
- The code includes tests for core functionality.
- The project can run with either a local Ollama model or an
  OpenAI-compatible API.

## License

This project is submitted as an assessment solution by Suman Behera.
