from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command


class StartCommand(Command):
    name="start"
    description = "Start the bot"


    async def execute(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.message is None:
            return
        await update.message.reply_text(
            "Hello! I'm your seconde-brain bot.\n\n"
            "Use /help to see available commands."
        )


