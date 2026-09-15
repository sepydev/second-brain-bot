from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.tasks.celery_app import celery_app


class ResearchCommand(Command):
    name = "research"
    description = "Start or show a research session"

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.message is None:
            return

        if not context.args:
            await update.message.reply_text(
                "Usage: /research <item_id>"
            )
            return

        try:
            item_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text(
                "The item ID must be a number."
            )
            return

        repository = context.application.bot_data["repository"]

        item = repository.get_research_item(item_id)

        if item is None:
            await update.message.reply_text(
                f"Research item #{item_id} was not found."
            )
            return

        chat_id = update.effective_chat.id
        session = repository.get_session_for_item(item_id)

        if session is None:
            repository.create_session(item_id, chat_id)
        else:
            repository.set_session_chat(session["id"], chat_id)

        repository.set_item_status(item_id, "researching")

        celery_app.send_task(
            "research.run_research",
            args=[item_id, chat_id],
        )

        await update.message.reply_text(
            f"Researching #{item_id}: {item['content']}\n"
            "Searching your knowledge base and the web in the "
            "background. I'll message you here when it's ready."
        )