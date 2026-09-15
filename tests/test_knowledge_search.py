from pathlib import Path

from second_brain_bot.knowledge.search import KnowledgeSearch


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_search_finds_matching_file_by_content(tmp_path: Path) -> None:
    _write(
        tmp_path / "django" / "orm" / "constraints.md",
        "Django ORM constraints let you enforce rules at the "
        "database level, such as CheckConstraint.",
    )
    _write(
        tmp_path / "python" / "generics.md",
        "Python generics allow parametrized typing.",
    )

    search = KnowledgeSearch(tmp_path)
    results = search.search("constraint in django", category="django")

    assert len(results) == 1
    assert results[0].path.name == "constraints.md"
    assert "CheckConstraint" in results[0].excerpt


def test_search_category_hint_filters_by_path(tmp_path: Path) -> None:
    _write(
        tmp_path / "django" / "orm" / "constraints.md",
        "constraint content",
    )
    _write(
        tmp_path / "sql" / "constraint.md",
        "constraint content",
    )

    search = KnowledgeSearch(tmp_path)
    results = search.search("constraint", category="django")

    assert len(results) == 1
    assert "django" in results[0].path.parts


def test_search_returns_empty_for_missing_root(tmp_path: Path) -> None:
    search = KnowledgeSearch(tmp_path / "does-not-exist")
    assert search.search("anything") == []


def test_search_returns_empty_without_terms(tmp_path: Path) -> None:
    search = KnowledgeSearch(tmp_path)
    assert search.search("  ") == []
