import re
from datetime import UTC, datetime
from pathlib import Path


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "untitled"


def write_knowledge_note(
    *,
    root: Path,
    category: str | None,
    topic: str,
    content: str,
) -> Path:
    first_category = (category or "").split(",")[0].strip()

    directory = root / first_category if first_category else root
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / f"{_slugify(topic)}.md"

    note = f"""---
topic: {topic}
category: {category or ""}
created_at: {datetime.now(UTC).isoformat()}
---

{content}
"""

    path.write_text(note, encoding="utf-8")

    return path
