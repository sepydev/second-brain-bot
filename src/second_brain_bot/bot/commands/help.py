from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command


class HelpCommand(Command):
    name="help"
    description ="Show this help"


    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        commands = context.application.bot_data["commands"]

        lines = [
            "Available commands:",
            "",
            *(
                f"/{command.name} - {command.description}"
                for command in commands
            ),
        ]

        await update.message.reply_text("\n".join(lines))