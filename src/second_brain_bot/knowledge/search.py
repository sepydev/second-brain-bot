"""
This first version deliberately uses simple local search.
No embeddings.
No vector database.
No LangChain.
No Kubernetes cluster deployed in your living room.

KnowledgeSearch
       │
       ├── keyword
       ├── FTS5
       ├── embeddings
       └── hybrid
       
"""
import re
from pathlib import Path

from second_brain_bot.knowledge.models import KnowledgeMatch


class KnowledgeSearch:
    def __init__(self, root: Path) -> None:
        self.root = root

    def search(
        self,
        query: str,
        *,
        category: str | None = None,
        limit: int = 5,
    ) -> list[KnowledgeMatch]:
        if not self.root.exists():
            return []

        terms = self._tokenize(query)

        if not terms:
            return []

        matches: list[KnowledgeMatch] = []

        for path in self.root.rglob("*.md"):
            if category and category.lower() not in {
                part.lower() for part in path.parts
            }:
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            score = self._score(
                path=path,
                content=content,
                terms=terms,
            )

            if score <= 0:
                continue

            matches.append(
                KnowledgeMatch(
                    path=path,
                    score=score,
                    excerpt=self._excerpt(content, terms),
                )
            )

        matches.sort(
            key=lambda match: match.score,
            reverse=True,
        )

        return matches[:limit]

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {
            token.lower()
            for token in re.findall(r"\b[\w-]+\b", text)
            if len(token) > 2
        }

    def _score(
        self,
        *,
        path: Path,
        content: str,
        terms: set[str],
    ) -> float:
        lower_content = content.lower()
        lower_path = str(path).lower()

        score = 0.0

        for term in terms:
            score += lower_content.count(term)
            score += 2 * lower_path.count(term)

        return score

    @staticmethod
    def _excerpt(
        content: str,
        terms: set[str],
        max_length: int = 1500,
    ) -> str:
        lines = content.splitlines()

        relevant_lines = [
            line
            for line in lines
            if any(term in line.lower() for term in terms)
        ]

        excerpt = "\n".join(relevant_lines)

        if not excerpt:
            excerpt = content[:max_length]

        return excerpt[:max_length]