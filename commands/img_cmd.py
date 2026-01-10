import logging
import time
import os
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError
from dotenv import load_dotenv
from ya_down import *
from commands.text_to_image import * 
from shared_state import *

load_dotenv()

logger = logging.getLogger(__name__)

async def send_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"Команда: /img, Пользователь: {user.full_name} (@{user.username or 'N/A'}), ID: {user.id}, Время: {time.strftime('%Y-%m-%d %H:%M:%S')}, Контекст: {prompt}")
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="⏳")
    if prompt:
        status, data = await generate_image(prompt, get_model_img())
    else:
        await update.message.reply_text("❌ Укажите описание")
    
    if status == "complete":
        simple_download_image(data.get('imageUrl'), "image.jpg")
        x = 5
        while x:
            try:
                with open("image.jpg", "rb") as img:
                    await update.message.reply_photo(img)
                x = 0
            except TelegramError as e:
                x -= 1
                print("ERROR")
                logger.error(f"Ошибка при отправке изображения: {e}")
        await delayed_remove("image")
    else:
        await update.message.reply_text("❌ Ошибка генерации. Попробуйте другую модель.")
    await loading_msg.delete()

async def ask_pmod(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from shared_state import MODEL_IMG, set_model_img
    models = await get_models_img()

    num = len(models)
    if update.message.text[5:].strip() == "":
        s = f'<b>Доступные модели</b>\n'
        for i, model_info in enumerate(models, 1):
            s = s + ''.join(f"\n{i}. Model: {model_info['model']}, Provider: {model_info['provider']}" if model_info['model'] == MODEL_IMG
                            else f"\n<b>{i}. Model: {model_info['model']}, Provider: {model_info['provider']}</b>")
        await update.message.reply_html(s)
    else:
        try:
            type = int(update.message.text[5:].strip())
            if 0 < type and type <= num:
                # Update the shared MODEL_IMG
                set_model_img(models[type-1]["model"])
                await update.message.reply_text(f"Текущая модель: {models[type-1]["model"]}")
            else:
                await update.message.reply_text(f"❌ Номер моедли должен быть от 1 до {num}")
        except:
            await update.message.reply_text(f"❌ Номер модели должен быть числом")