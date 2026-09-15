from second_brain_bot.web.search import WebSearch


def test_search_returns_web_sources() -> None:
    def fake_search(query: str, limit: int):
        return [
            {"title": "Result 1", "href": "https://example.com/1"},
            {"title": "Result 2", "href": "https://example.com/2"},
        ]

    def fake_fetch(url: str) -> str:
        return f"<html><body><p>content for {url}</p></body></html>"

    search = WebSearch(search_fn=fake_search, fetch_fn=fake_fetch)
    sources = search.search("cqrs", limit=5)

    assert len(sources) == 2
    assert sources[0].title == "Result 1"
    assert sources[0].url == "https://example.com/1"
    assert "content for https://example.com/1" in sources[0].content


def test_search_skips_failed_fetches() -> None:
    def fake_search(query: str, limit: int):
        return [
            {"title": "Bad", "href": "https://example.com/bad"},
            {"title": "Good", "href": "https://example.com/good"},
        ]

    def fake_fetch(url: str) -> str:
        if "bad" in url:
            raise RuntimeError("network error")
        return "<html><body>ok</body></html>"

    search = WebSearch(search_fn=fake_search, fetch_fn=fake_fetch)
    sources = search.search("cqrs")

    assert len(sources) == 1
    assert sources[0].url == "https://example.com/good"


def test_search_returns_empty_on_search_failure() -> None:
    def fake_search(query: str, limit: int):
        raise RuntimeError("ddg is down")

    search = WebSearch(search_fn=fake_search, fetch_fn=lambda url: "")

    assert search.search("cqrs") == []
