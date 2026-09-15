"""
This is the one piece we should connect to an actual search provider next.
The important architectural point is that:
WebSearch
returns sources.
It does not ask Qwen to search.
"""
import re
from collections.abc import Callable, Iterable

import httpx
from bs4 import BeautifulSoup
from ddgs import DDGS

from second_brain_bot.web.models import WebSource

USER_AGENT = (
    "Mozilla/5.0 (compatible; second-brain-bot/0.1; "
    "+https://github.com/mrprocs/second-brain-bot)"
)


def _default_search(query: str, limit: int) -> Iterable[dict]:
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=limit))


def _default_fetch(url: str) -> str:
    response = httpx.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=10.0,
        follow_redirects=True,
    )
    response.raise_for_status()

    return response.text


def _extract_text(html: str, max_length: int = 3000) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text).strip()

    return text[:max_length]


class WebSearch:
    def __init__(
        self,
        *,
        search_fn: Callable[[str, int], Iterable[dict]] = _default_search,
        fetch_fn: Callable[[str], str] = _default_fetch,
    ) -> None:
        self.search_fn = search_fn
        self.fetch_fn = fetch_fn

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[WebSource]:
        try:
            results = self.search_fn(query, limit)
        except Exception:
            return []

        sources: list[WebSource] = []

        for result in results:
            url = result.get("href") or result.get("url")

            if not url:
                continue

            try:
                html = self.fetch_fn(url)
            except Exception:
                continue

            content = _extract_text(html)

            if not content:
                continue

            sources.append(
                WebSource(
                    title=result.get("title", url),
                    url=url,
                    content=content,
                )
            )

            if len(sources) >= limit:
                break

        return sources
