from telegram import Update
from telegram.ext import (
    Application,
)

from second_brain_bot.bot.registery import register_commands
from second_brain_bot.config import settings
from second_brain_bot.database.connection import create_connection
from second_brain_bot.database.repository import initialize_database


def main() -> None:
    database = create_connection(settings.database_path)
    initialize_database(database)

    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )

    application.bot_data["database"] = database
    commands = register_commands(application)
    application.bot_data["commands"] = commands

    print("Bot is running...")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()