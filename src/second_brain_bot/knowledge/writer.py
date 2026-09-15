import re
from datetime import UTC, datetime
from pathlib import Path

from second_brain_bot.knowledge.models import KnowledgeMatch

MIN_MATCH_SCORE = 2.0


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def resolve_target_directory(
    *,
    root: Path,
    category: str | None,
    matches: list[KnowledgeMatch],
) -> Path:
    """Prefer the folder of the strongest existing knowledge match, since
    that means the vault already has a place for this topic. Fall back to
    the category-as-folder hint only when no such match exists.
    """
    if matches and matches[0].score >= MIN_MATCH_SCORE:
        return matches[0].path.parent

    first_category = (category or "").split(",")[0].strip()

    return root / first_category if first_category else root


def write_knowledge_note(
    *,
    target_directory: Path,
    category: str | None,
    topic: str,
    content: str,
) -> Path:
    target_directory.mkdir(parents=True, exist_ok=True)

    path = target_directory / f"{_slugify(topic)}.md"

    note = f"""---
topic: {topic}
category: {category or ""}
created_at: {datetime.now(UTC).isoformat()}
---

{content}
"""

    path.write_text(note, encoding="utf-8")

    return path
