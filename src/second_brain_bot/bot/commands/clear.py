from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command


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

        repository = context.application.bot_data["repository"]

        repository.clear_research_items()

        await update.message.reply_text("All Items deleted.")