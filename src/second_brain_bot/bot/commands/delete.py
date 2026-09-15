from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command


class DeleteCommand(Command):
    name = "delete"
    description = "Delete an item"

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if update.message is None:
            return

        repository = context.application.bot_data["repository"]

        id = context.args[0]

        repository.delete_research_item(id)

        await update.message.reply_text("Selected item deleted.")