from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command


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

        repository = context.application.bot_data["repository"]

        items =repository.list_research_items()

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