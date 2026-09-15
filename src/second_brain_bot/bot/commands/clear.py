from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.database.repository import clear_items


class ClearCommand(Command):
    name = "clear"
    description = "Clear all Items"

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if update.message is None:
            return

        database = context.application.bot_data["database"]

        clear_items(database)

        await update.message.reply_text("All Items deleted.")