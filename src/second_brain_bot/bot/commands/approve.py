from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.bot.command import Command
from second_brain_bot.config import settings
from second_brain_bot.knowledge.writer import write_knowledge_note


class ApproveCommand(Command):
    name = "approve"
    description = "Approve the current research result"

    async def execute(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if update.message is None:
            return

        chat_id = update.effective_chat.id
        repository = context.application.bot_data["repository"]

        session = repository.get_active_session_for_chat(chat_id)

        if session is None:
            await update.message.reply_text(
                "No active research session."
            )
            return

        item = repository.get_research_item(session["research_item_id"])

        if item is None:
            await update.message.reply_text(
                "Research item not found."
            )
            return

        if not item["research"]:
            await update.message.reply_text(
                "This item has no research result yet. "
                "Use /research first."
            )
            return

        if item["status"] == "approved":
            await update.message.reply_text(
                "This research is already approved."
            )
            return

        path = write_knowledge_note(
            root=settings.second_brain_path,
            category=item["category"],
            topic=item["content"],
            content=item["research"],
        )

        repository.approve_research_item(item["id"])

        relative_path = path.relative_to(settings.second_brain_path)

        await update.message.reply_text(
            f"Research approved and saved to {relative_path}"
        )
