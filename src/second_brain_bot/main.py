from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
)

from second_brain_bot.bot.handlers import add_command, help_command, list_command, start
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
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("list", list_command))

    print("Bot is running...")

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()