from telegram.ext import Application, MessageHandler, filters

from second_brain_bot.bot.message_handler import handle_message
from second_brain_bot.bot.registry import register_commands
from second_brain_bot.config import settings
from second_brain_bot.database.connection import create_connection, initialize_database
from second_brain_bot.database.repository import ResearchRepository


def main() -> None:
    connection = create_connection(
        settings.database_path
    )
    initialize_database(connection)

    repository = ResearchRepository(connection)

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    commands = register_commands(application)

    application.bot_data["repository"] = repository
    application.bot_data["commands"] = commands

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
    print("Bot is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
