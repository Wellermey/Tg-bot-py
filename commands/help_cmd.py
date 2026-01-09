import logging
import time
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user = update.effective_user
    await update.message.reply_html(

        rf""" 
<b>Доступные команды:</b>
/hi - пишет Хай!
/ai - отвечает на промпт
/mod - выбор модели
/clear - очистка истории
        """

    )