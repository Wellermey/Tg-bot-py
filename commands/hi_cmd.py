from telegram import Update
from telegram.ext import ContextTypes

async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "Хай!"
    )