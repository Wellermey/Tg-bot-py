import logging
import time
from telegram import Update
from telegram.ext import ContextTypes
from jokes import get_random_cached_joke

logger = logging.getLogger(__name__)

# Global counter for jokes
num = 0

async def send_random_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global num
    logger.info(f"Получена команда /joke от {update.effective_user.full_name}")
    joke = await get_random_cached_joke(num)
    await update.message.reply_text(joke)
    num = (num % 10) + 1