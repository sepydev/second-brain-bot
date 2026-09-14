from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.database.repository import add_item


class AddCommand(Command):
    name = "add"
    description = "Add a research item"

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.message is None:
            return

        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /add <keyword> <category>"
            )
            return

        category = context.args[-1]
        keyword = " ".join(context.args[:-1])

        database = context.application.bot_data["database"]

        item_id = add_item(
            database,
            keyword=keyword,
            category=category,
        )

        await update.message.reply_text(
            f"Added #{item_id}: {keyword} [{category}]"
        )