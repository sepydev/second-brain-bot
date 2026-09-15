from dataclasses import dataclass

from second_brain_bot.knowledge.models import KnowledgeMatch
from second_brain_bot.web.models import WebSource


@dataclass(frozen=True)
class ResearchContext:
    topic: str
    category: str | None
    knowledge: list[KnowledgeMatch]
    sources: list[WebSource]


@dataclass(frozen=True)
class ResearchResult:
    answer: str
    context: ResearchContext