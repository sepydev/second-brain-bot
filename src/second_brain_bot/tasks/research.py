import asyncio
import logging
from dataclasses import dataclass

from celery.signals import worker_process_init
from telegram import Bot
from telegram.constants import MessageLimit
from telegram.error import NetworkError, TimedOut
from telegram.request import HTTPXRequest

from second_brain_bot.config import settings
from second_brain_bot.database.connection import create_connection, initialize_database
from second_brain_bot.database.repository import ResearchRepository
from second_brain_bot.knowledge.search import KnowledgeSearch
from second_brain_bot.llm.models import ChatMessage
from second_brain_bot.llm.ollama import OllamaClient
from second_brain_bot.research.service import ResearchService
from second_brain_bot.tasks.celery_app import celery_app
from second_brain_bot.web.search import WebSearch


@dataclass
class WorkerServices:
    repository: ResearchRepository
    llm: OllamaClient
    research_service: ResearchService


logger = logging.getLogger(__name__)

_services: WorkerServices | None = None


def _build_services() -> WorkerServices:
    connection = create_connection(settings.database_path)
    initialize_database(connection)

    repository = ResearchRepository(connection)
    llm = OllamaClient()

    research_service = ResearchService(
        knowledge_search=KnowledgeSearch(settings.second_brain_path),
        web_search=WebSearch(),
        llm=llm,
    )

    return WorkerServices(
        repository=repository,
        llm=llm,
        research_service=research_service,
    )


@worker_process_init.connect
def _on_worker_process_init(**kwargs) -> None:
    global _services
    _services = _build_services()


def _get_services() -> WorkerServices:
    global _services

    if _services is None:
        _services = _build_services()

    return _services


NOTIFY_RETRIES = 3


def _notify(chat_id: int, text: str) -> None:
    async def _send() -> None:
        request = HTTPXRequest(
            connect_timeout=15.0,
            read_timeout=30.0,
            write_timeout=30.0,
        )
        bot = Bot(token=settings.telegram_bot_token, request=request)

        chunk_size = MessageLimit.MAX_TEXT_LENGTH

        async with bot:
            for start in range(0, len(text), chunk_size):
                chunk = text[start : start + chunk_size]

                for attempt in range(1, NOTIFY_RETRIES + 1):
                    try:
                        await bot.send_message(chat_id=chat_id, text=chunk)
                        break
                    except (TimedOut, NetworkError):
                        if attempt == NOTIFY_RETRIES:
                            raise
                        await asyncio.sleep(attempt)

    try:
        asyncio.run(_send())
    except (TimedOut, NetworkError):
        logger.exception(
            "Failed to notify chat %s after %d attempts",
            chat_id,
            NOTIFY_RETRIES,
        )


@celery_app.task(name="research.run_research")
def run_research(item_id: int, chat_id: int) -> None:
    services = _get_services()
    repository = services.repository

    repository.set_item_status(item_id, "researching")

    item = repository.get_research_item(item_id)

    if item is None:
        _notify(chat_id, f"Research item #{item_id} was not found.")
        return

    try:
        result = services.research_service.research(
            topic=item["content"],
            category=item["category"],
        )
    except Exception as exc:
        repository.set_item_error(item_id, str(exc))
        _notify(
            chat_id,
            f"Research on #{item_id} failed: {exc}",
        )
        return

    session = repository.get_session_for_item(item_id)

    if session is not None:
        repository.add_message(session["id"], "assistant", result.answer)

    repository.update_research(item_id, result.answer)

    _notify(
        chat_id,
        f"Research on #{item_id}: {item['content']}\n\n"
        f"{result.answer}\n\n"
        "Ask follow-up questions here, or use /approve to save this "
        "to your knowledge base.",
    )


@celery_app.task(name="research.run_followup")
def run_followup(session_id: int, chat_id: int) -> None:
    services = _get_services()
    repository = services.repository

    session = repository.get_session(session_id)

    if session is None:
        _notify(chat_id, "Research session not found.")
        return

    messages = repository.get_messages(session_id)

    llm_messages = [
        ChatMessage(
            role="system",
            content=(
                "You are continuing a research conversation. "
                "Use the existing research context and answer "
                "the user's question accurately."
            ),
        ),
        *[
            ChatMessage(
                role=message["role"],
                content=message["content"],
            )
            for message in messages
        ],
    ]

    try:
        answer = services.llm.chat(llm_messages)
    except Exception as exc:
        _notify(chat_id, f"Follow-up failed: {exc}")
        return

    repository.add_message(session_id, "assistant", answer)
    repository.update_research(session["research_item_id"], answer)

    _notify(chat_id, answer)
