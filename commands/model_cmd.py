import logging
import time
from telegram import Update
from telegram.ext import ContextTypes
from router_models import get_models
from shared_state import MODEL_ID

logger = logging.getLogger(__name__)

async def ask_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from shared_state import MODEL_ID, set_model_id
    num, models = get_models()

    if update.message.text[4:].strip() == "":
        s = f'<b>Найдено моделей: {num}</b>\n'
        s = s + ''.join([f'{i+1}) {models[i][1]}\n'.replace('(free)','') if models[i][0] != MODEL_ID 
                         else f'<b>{i+1}) {models[i][1]}</b>\n'.replace('(free)','')  for i in range(num)])
        s = s.rstrip('\n')
        await update.message.reply_html(s)
    else:
        try:
            type = int(update.message.text[4:].strip())
            if 0 < type and type <= num:
                # Update the shared MODEL_ID
                set_model_id(models[type-1][0])
                await update.message.reply_text(f"Текущая модель: {models[type-1][1]}")
            else:
                await update.message.reply_text(f"❌ Номер моедли должен быть от 1 до {num}")
        except:
            await update.message.reply_text(f"❌ Номер модели должен быть числом")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Clear the shared context messages
    from shared_state import clear_context
    clear_context()
    await update.message.reply_text("История очищена!")