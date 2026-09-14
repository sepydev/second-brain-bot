from telegram import Update
from telegram.ext import ContextTypes

from second_brain_bot.database.repository import add_item, list_items


async def start(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return
    await update.message.reply_text(
        "Hello! I'm your seconde-brain bot.\n\n"
        "Use /help to see available commands."
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    await update.message.reply_text(
        "Second Brain Bot\n\n"
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help\n"
        "/add <keyword> <category> - Add a research item\n\n"
        "Example:\n"
        "/add CQRS architecture"
    )



async def add_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /add <keyword> <category>\n\n"
            "Example:\n"
            "/add CQRS architecture"
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


async def list_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
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
            f"#{item['id']} {item['keyword']} "
            f"[{item['category']}] - {item['status']}"
        )

    await update.message.reply_text("\n".join(lines))