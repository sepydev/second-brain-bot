from pathlib import Path

from second_brain_bot.knowledge.writer import _slugify, write_knowledge_note


def test_slugify() -> None:
    assert _slugify("CQRS architecture") == "cqrs-architecture"
    assert _slugify("  weird!! Chars??  ") == "weird-chars"
    assert _slugify("") == "untitled"


def test_write_knowledge_note_uses_first_category_as_folder(
    tmp_path: Path,
) -> None:
    path = write_knowledge_note(
        root=tmp_path,
        category="architecture,patterns",
        topic="CQRS architecture",
        content="CQRS separates reads from writes.",
    )

    assert path == tmp_path / "architecture" / "cqrs-architecture.md"
    text = path.read_text(encoding="utf-8")
    assert "topic: CQRS architecture" in text
    assert "CQRS separates reads from writes." in text


def test_write_knowledge_note_without_category_uses_root(
    tmp_path: Path,
) -> None:
    path = write_knowledge_note(
        root=tmp_path,
        category="",
        topic="DDD",
        content="content",
    )

    assert path == tmp_path / "ddd.md"


def test_write_knowledge_note_overwrites_existing(tmp_path: Path) -> None:
    write_knowledge_note(
        root=tmp_path,
        category="",
        topic="DDD",
        content="first version",
    )
    path = write_knowledge_note(
        root=tmp_path,
        category="",
        topic="DDD",
        content="second version",
    )

    text = path.read_text(encoding="utf-8")
    assert "second version" in text
    assert "first version" not in text
