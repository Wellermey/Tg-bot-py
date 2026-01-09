import logging
import time
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from dotenv import load_dotenv
from ya_down import *

load_dotenv()

logger = logging.getLogger(__name__)

YA_TOKEN = os.getenv("YA_TOKEN")

async def send_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_name = " ".join(context.args)
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"Команда: /music, Пользователь: {user.full_name} (@{user.username or 'N/A'}), ID: {user.id}, Время: {time.strftime('%Y-%m-%d %H:%M:%S')}, Контекст: {track_name}")
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="⏳")
    
    err = await get_track(track_name)
    
    if err == 1:
        await update.message.reply_text("❌ Укажите название трека.")
    
    if err != 2:
        print(err)
        artists = ' / '.join(err[1])
        x = 5
        while x:
            try:
                await update.message.reply_audio(
                    audio=f'{err[0]}.mp3',
                    thumbnail=f'{err[0]}.jpg',
                    performer=artists,
                    title=err[0]
                )
                x = 0
            except TelegramError as e:
                x -= 1
                print("ERROR")
                logger.error(f"Ошибка при отправке аудио: {e}")
        await delayed_remove(err[0])
    else:
        await update.message.reply_text("❌ Трек не найден.")
    await loading_msg.delete()