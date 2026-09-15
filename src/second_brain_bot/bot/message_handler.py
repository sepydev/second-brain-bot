from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.tasks.celery_app import celery_app


async def handle_message(
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
            "No active research session. "
            "Use /research <item_id> first."
        )
        return

    user_text = update.message.text

    repository.add_message(
        session["id"],
        "user",
        user_text,
    )

    celery_app.send_task(
        "research.run_followup",
        args=[session["id"], chat_id],
    )

    await update.message.reply_text("Thinking...")
