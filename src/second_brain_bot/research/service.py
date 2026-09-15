"""
This is the first important milestone.
Notice what it doesn't do:
❌ Telegram
❌ SQLite
❌ Markdown writing
❌ Ollama-specific code
That's deliberate.
"""
from second_brain_bot.knowledge.search import KnowledgeSearch
from second_brain_bot.llm.client import LLMClient
from second_brain_bot.llm.models import ChatMessage
from second_brain_bot.research.models import (
    ResearchContext,
    ResearchResult,
)
from second_brain_bot.research.prompts import build_research_prompt
from second_brain_bot.web.search import WebSearch


class ResearchService:
    def __init__(
        self,
        *,
        knowledge_search: KnowledgeSearch,
        web_search: WebSearch,
        llm: LLMClient,
    ) -> None:
        self.knowledge_search = knowledge_search
        self.web_search = web_search
        self.llm = llm

    def research(
        self,
        *,
        topic: str,
        category: str | None,
    ) -> ResearchResult:
        knowledge = self.knowledge_search.search(
            topic,
            category=category,
        )

        sources = self.web_search.search(topic)

        context = ResearchContext(
            topic=topic,
            category=category,
            knowledge=knowledge,
            sources=sources,
        )

        prompt = build_research_prompt(context)

        answer = self.llm.chat(
            [
                ChatMessage(
                    role="user",
                    content=prompt,
                )
            ]
        )

        return ResearchResult(
            answer=answer,
            context=context,
        )