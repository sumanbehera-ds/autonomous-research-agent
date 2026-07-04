from research_agent import cli


def test_shorthand_topic_can_start_with_history():
    assert cli._normalize_argv(["history", "of", "AI"]) == ["run", "history", "of", "AI"]


def test_shorthand_topic_can_start_with_show():
    assert cli._normalize_argv(["show", "me", "AI", "trends"]) == [
        "run",
        "show",
        "me",
        "AI",
        "trends",
    ]


def test_explicit_history_command_is_preserved():
    assert cli._normalize_argv(["history"]) == ["history"]
    assert cli._normalize_argv(["history", "--limit", "5"]) == ["history", "--limit", "5"]


def test_explicit_show_command_is_preserved():
    assert cli._normalize_argv(["show", "1"]) == ["show", "1"]
    assert cli._normalize_argv(["show", "--memory-db", "memory.sqlite3", "1"]) == [
        "show",
        "--memory-db",
        "memory.sqlite3",
        "1",
    ]


def test_main_routes_history_topic_to_run(monkeypatch):
    called = {}

    def fake_run(args):
        called["topic"] = args.topic
        return 0

    monkeypatch.setattr(cli, "command_run", fake_run)

    assert cli.main(["history", "of", "AI"]) == 0
    assert called["topic"] == ["history", "of", "AI"]
