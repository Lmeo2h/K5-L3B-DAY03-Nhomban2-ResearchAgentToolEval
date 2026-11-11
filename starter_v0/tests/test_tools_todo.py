"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["Sam Altman", "Elon Musk"]
    result = TOOL_FUNCTIONS["clarify"](question="Bạn muốn xem tài khoản nào?", response_type="choice", options=options)

    assert result["options"] == ["Sam Altman", "Elon Musk"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]
    markdown = TOOL_FUNCTIONS["format"](items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"tin {i}", "url": f"https://x.com/{i}"} for i in range(3)]
    markdown = TOOL_FUNCTIONS["format"](items=items, template="thread")["markdown"]

    lines = [line for line in markdown.split("\n") if line.strip()]
    assert [line.split(" ")[0] for line in lines] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty, template="sections")
        assert result["item_count"] == 0
        assert isinstance(result["markdown"], str)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:fake-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100999")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin AI", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "123:fake-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100999"
    assert calls[0]["json"]["text"] == "Bản tin AI"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin AI", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"](query="AI", topic="general", timeframe=None)

    assert len(calls) == 1
    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["topic"] == "general"


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "Nội dung bài viết",
        "metadata": {"title": "T", "sourceURL": "https://www.openai.com/research/x"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://www.openai.com/research/x")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.openai.com/research/x"
    assert result["items"][0] == {
        "title": "T",
        "url": "https://www.openai.com/research/x",
        "source": "openai.com",
        "summary": "Nội dung bài viết",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    summary = TOOL_FUNCTIONS["fetch"](url="https://example.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk-test")
    raw = [{"text": "no id", "screen_name": "sama"}] + [
        {"tweet_id": str(100 + i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)
    ]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    assert [item["url"] for item in result["items"]] == [
        "https://x.com/sama/status/100", "https://x.com/sama/status/101", "https://x.com/sama/status/102",
    ]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rk-test")
    calls = fake_http(FakeResponse({"timeline": []}))

    for search_type in ("Top", "Latest"):
        TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type=search_type)

    assert [c["params"] for c in calls] == [
        {"query": "OpenAI", "search_type": "Top"},
        {"query": "OpenAI", "search_type": "Latest"},
    ]
    assert calls[0]["url"].endswith("/search.php")


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    for empty in ("", "   ", "?!"):
        assert TOOL_FUNCTIONS["policy"](query=empty)["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = TOOL_FUNCTIONS["policy"](query="API key dữ liệu khách hàng prompt", policy_area="data_privacy", top_k=5)["results"]

    assert results
    assert all(item["policy_area"] == "data_privacy" for item in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = TOOL_FUNCTIONS["policy"](query="injection probe citation", policy_area="source_citation", top_k=10)["results"]
    probe = [item for item in results if item["section"] == "Injection probe"]

    assert probe, "the Injection probe section should be retrieved"
    assert any("viral tweet" in line for line in probe[0]["untrusted_text"])
    assert "viral tweet" not in probe[0]["facts"]


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

wiki_tool = TOOL_FUNCTIONS["wiki"]


def test_wiki_happy_path_builds_request_and_maps_summary(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "OpenAI",
        "extract": "OpenAI is an AI research organization.",
        "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/OpenAI"}},
    }))

    result = wiki_tool(title="Large language model", lang="en")

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://en.wikipedia.org/api/rest_v1/page/summary/Large_language_model"
    assert "User-Agent" in calls[0]["headers"]
    assert result["items"] == [{
        "title": "OpenAI",
        "url": "https://en.wikipedia.org/wiki/OpenAI",
        "source": "en.wikipedia.org",
        "summary": "OpenAI is an AI research organization.",
    }]


def test_wiki_empty_title_returns_error_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    for bad in ("", "   ", None, 123):
        result = wiki_tool(title=bad)
        assert result["error"] == "ValueError"
    assert calls == []


def test_wiki_lang_outside_enum_returns_error_without_network(fake_http) -> None:
    calls = fake_http(FakeResponse({}))
    result = wiki_tool(title="OpenAI", lang="fr")
    assert result["error"] == "ValueError"
    assert "lang" in result["message"]
    assert calls == []


def test_wiki_missing_article_404_returns_not_found_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))
    result = wiki_tool(title="Khong co bai nay")
    assert result["error"] == "NotFound"
    assert result["items"] == []


def test_wiki_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))
    result = wiki_tool(title="OpenAI")
    assert result["error"] == "HTTPError"


def test_wiki_network_exception_returns_error_dict(fake_http) -> None:
    import requests
    fake_http(requests.ConnectionError("down"))
    result = wiki_tool(title="OpenAI")
    assert result["error"] == "ConnectionError"
