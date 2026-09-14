from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.database.repository import list_items


class ListCommand(Command):
    name = "list"
    description = "List research items"

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if update.message is None:
            return

        database = context.application.bot_data["database"]

        items = list_items(database)

        if not items:
            await update.message.reply_text(
                "Research inbox is empty."
            )
            return

        lines = ["Research inbox:\n"]

        for item in items:
            lines.append(
                f"#{item['id']} {item['content']} "
                f"[{item['category']}] - {item['status']}"
            )

        await update.message.reply_text("\n".join(lines))