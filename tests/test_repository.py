import sqlite3

import pytest

from second_brain_bot.database.connection import initialize_database
from second_brain_bot.database.repository import ResearchRepository


@pytest.fixture
def repository() -> ResearchRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    initialize_database(connection)

    return ResearchRepository(connection)


def test_add_list_delete_clear(repository: ResearchRepository) -> None:
    item_id = repository.add_research_item(
        content="CQRS architecture",
        category="architecture",
    )

    items = repository.list_research_items()
    assert len(items) == 1
    assert items[0]["content"] == "CQRS architecture"
    assert items[0]["status"] == "inbox"

    repository.delete_research_item(str(item_id))
    assert repository.list_research_items() == []

    second_id = repository.add_research_item(content="DDD", category="")
    repository.add_research_item(content="Event sourcing", category="")
    assert len(repository.list_research_items()) == 2

    repository.clear_research_items()
    assert repository.list_research_items() == []
    assert repository.get_research_item(second_id) is None


def test_session_chat_tracking(repository: ResearchRepository) -> None:
    item_id = repository.add_research_item(content="CQRS", category="")

    assert repository.get_active_session_for_chat(chat_id=42) is None

    session_id = repository.create_session(item_id, chat_id=42)

    session = repository.get_active_session_for_chat(chat_id=42)
    assert session is not None
    assert session["id"] == session_id
    assert session["chat_id"] == 42

    repository.set_session_chat(session_id, chat_id=99)
    session = repository.get_active_session_for_chat(chat_id=99)
    assert session is not None
    assert session["id"] == session_id

    assert repository.get_active_session_for_chat(chat_id=42) is None


def test_item_status_transitions(repository: ResearchRepository) -> None:
    item_id = repository.add_research_item(content="CQRS", category="")

    repository.set_item_status(item_id, "researching")
    item = repository.get_research_item(item_id)
    assert item is not None
    assert item["status"] == "researching"

    repository.update_research(item_id, "the answer")
    item = repository.get_research_item(item_id)
    assert item is not None
    assert item["status"] == "review"
    assert item["research"] == "the answer"

    repository.approve_research_item(item_id)
    item = repository.get_research_item(item_id)
    assert item is not None
    assert item["status"] == "approved"


def test_item_error(repository: ResearchRepository) -> None:
    item_id = repository.add_research_item(content="CQRS", category="")

    repository.set_item_error(item_id, "boom")

    item = repository.get_research_item(item_id)
    assert item is not None
    assert item["status"] == "failed"
    assert item["research_error"] == "boom"


def test_messages(repository: ResearchRepository) -> None:
    item_id = repository.add_research_item(content="CQRS", category="")
    session_id = repository.create_session(item_id, chat_id=1)

    repository.add_message(session_id, "user", "why cqrs?")
    repository.add_message(session_id, "assistant", "because reasons")

    messages = repository.get_messages(session_id)
    assert [dict(message) for message in messages] == [
        {"role": "user", "content": "why cqrs?"},
        {"role": "assistant", "content": "because reasons"},
    ]
