from research_agent.utils import normalize_url, parse_json_object, slugify


def test_slugify_keeps_filename_safe_text():
    assert slugify("Agentic AI: Cybersecurity Trends!") == "agentic-ai-cybersecurity-trends"


def test_parse_json_object_handles_fenced_json():
    data = parse_json_object('```json\n{"answer": 42}\n```')
    assert data == {"answer": 42}


def test_normalize_duckduckgo_redirect():
    url = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fpage"
    assert normalize_url(url) == "https://example.com/page"
