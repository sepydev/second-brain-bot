from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.database.repository import add_item


class AddCommand(Command):
    name = "add"
    description = "Add a research item"

    def _parse_add_args(self, args: list[str]) -> tuple[str, str ]:
        categories = []
        content_args = []

        index = 0

        while index < len(args):
            if args[index] == "--category" or args[index]== "-c":
                index += 1
                categories = args[index: ]
                continue

            content_args.append(args[index])
            index += 1

        content = " ".join(content_args)

        if not content:
            raise ValueError("Content is required")

        return content, ",".join(categories)

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.message is None:
            return

        content, category = self._parse_add_args(context.args[:])


        database = context.application.bot_data["database"]

        item_id = add_item(
            database,
            content=content,
            category=category,
        )

        await update.message.reply_text(
            f"Added #{item_id}: {content} [{category}]"
        )