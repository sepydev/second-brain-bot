import pytest

from second_brain_bot.bot.commands.add import AddCommand


@pytest.fixture
def command() -> AddCommand:
    return AddCommand()


def test_parse_content_without_category(command: AddCommand) -> None:
    content, category = command._parse_add_args(
        ["CQRS", "architecture"]
    )

    assert content == "CQRS architecture"
    assert category == ""


def test_parse_content_with_single_category(command: AddCommand) -> None:
    content, category = command._parse_add_args(
        ["CQRS", "architecture", "--category", "architecture"]
    )

    assert content == "CQRS architecture"
    assert category == "architecture"


def test_parse_content_with_multiple_categories(command: AddCommand) -> None:
    content, category = command._parse_add_args(
        ["CQRS", "-c", "architecture", "patterns"]
    )

    assert content == "CQRS"
    assert category == "architecture,patterns"


def test_parse_raises_without_content(command: AddCommand) -> None:
    with pytest.raises(ValueError):
        command._parse_add_args(["--category", "architecture"])
