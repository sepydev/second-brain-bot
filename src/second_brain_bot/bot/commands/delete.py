from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.database.repository import delete_item


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

        database = context.application.bot_data["database"]

        id = context.args[0]

        delete_item(database, id)

        await update.message.reply_text("Selected item deleted.")