from pathlib import Path

from second_brain_bot.knowledge.models import KnowledgeMatch
from second_brain_bot.knowledge.writer import (
    _slugify,
    resolve_target_directory,
    write_knowledge_note,
)


def test_slugify() -> None:
    assert _slugify("CQRS architecture") == "cqrs-architecture"
    assert _slugify("  weird!! Chars??  ") == "weird-chars"
    assert _slugify("") == "untitled"


def test_write_knowledge_note_writes_into_target_directory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "architecture"

    path = write_knowledge_note(
        target_directory=target,
        category="architecture,patterns",
        topic="CQRS architecture",
        content="CQRS separates reads from writes.",
    )

    assert path == target / "cqrs-architecture.md"
    text = path.read_text(encoding="utf-8")
    assert "topic: CQRS architecture" in text
    assert "CQRS separates reads from writes." in text


def test_write_knowledge_note_overwrites_existing(tmp_path: Path) -> None:
    write_knowledge_note(
        target_directory=tmp_path,
        category="",
        topic="DDD",
        content="first version",
    )
    path = write_knowledge_note(
        target_directory=tmp_path,
        category="",
        topic="DDD",
        content="second version",
    )

    text = path.read_text(encoding="utf-8")
    assert "second version" in text
    assert "first version" not in text


def test_resolve_target_directory_prefers_strong_existing_match(
    tmp_path: Path,
) -> None:
    existing_folder = tmp_path / "django" / "orm"
    match = KnowledgeMatch(
        path=existing_folder / "constraints.md",
        score=5.0,
        excerpt="...",
    )

    target = resolve_target_directory(
        root=tmp_path,
        category="django",
        matches=[match],
    )

    assert target == existing_folder


def test_resolve_target_directory_falls_back_without_strong_match(
    tmp_path: Path,
) -> None:
    weak_match = KnowledgeMatch(
        path=tmp_path / "unrelated" / "note.md",
        score=0.5,
        excerpt="...",
    )

    target = resolve_target_directory(
        root=tmp_path,
        category="architecture,patterns",
        matches=[weak_match],
    )

    assert target == tmp_path / "architecture"


def test_resolve_target_directory_falls_back_without_category_or_matches(
    tmp_path: Path,
) -> None:
    target = resolve_target_directory(
        root=tmp_path,
        category="",
        matches=[],
    )

    assert target == tmp_path
