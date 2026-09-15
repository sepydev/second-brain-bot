from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeMatch:
    path: Path
    score: float
    excerpt: str