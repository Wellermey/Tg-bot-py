import logging
import asyncio
import aiohttp
import json
import time
import base64   
from telegram import *
from telegram.ext import *
from telegram.error import *
import os
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler('bot.log', encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

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

async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "Хай!"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Произошла ошибка при обработке обновления:", exc_info=context.error)

API_TOKEN = os.getenv("API_TOKEN")
system_prompt = ""
MODEL_ID = "tngtech/deepseek-r1t2-chimera:free"
API_URL = f"https://openrouter.ai/api/v1/chat/completions"

context_messages = [] # Список словарей вида {"role": "user", "content": "..."} или {"role": "assistant", "content": "..."}

async def gen_mesage_hug(prompt):
    global context_messages
    if len(context_messages) > 5:
        context_messages = context_messages[-5:]
    context_str = "Старые сообщения:"+'\n'.join(context_messages)
    context_messages.append(f"\nПользователь: {prompt}")
    context_str = context_str + f"\nНовое сообщение: {prompt}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}", 
    }
    data = {
        "model": MODEL_ID,
        "stream": False,
        "max_tokens": 1024,
        "messages": [
            {
            "role": "system",
            "content":"Ты - ассистент в Telegram-боте. Отвечай на вопросы пользователя. Форматируй свой ответ для Telegram в html. Можно использовать только такие теги b, i, code, s, u, pre language="". Не используй таблицы. Если промпт на музыкальную тему можно прикрепить ровно один музыкальный трек с помощью тега (обязательно в конце ответа) <song> название трека и исполнитель </song>",
            },
            {
            "role": "user",
            "content": context_str,
            },
        ],
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(API_URL, headers=headers, json=data) as response:
                response_status = response.status
                response_text = await response.text()

                if response_status == 200:
                    try:
                        output = json.loads(response_text)
                        bot_response = output['choices'][0]['message']['content']

                        clean_response = bot_response
                        if '</think>' in bot_response:
                            clean_response = bot_response[bot_response.find('</think>') + 8:].strip()
                        context_messages.append(f"Bot: {clean_response}")
                        return clean_response
                    except (json.JSONDecodeError, KeyError, IndexError) as parse_error:
                        logger.error(f"Ошибка парсинга JSON ответа: {parse_error}, ответ: {response_text}")
                        return f"Ошибка при обработке ответа модели: {parse_error}"
                else:
                    logger.error(f"Ошибка API: статус {response_status}, ответ: {response_text}")
                    return f"Ошибка API: статус {response_status}. Ответ: {response_text}"

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка HTTP запроса: {e}")
            return f"Ошибка при запросе к API: {e}"
        except Exception as e:
            logger.error(f"Неизвестная ошибка при запросе: {e}", exc_info=True)
            return f"Произошла ошибка при запросе к API: {e}"


async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(MODEL_ID)
    if update.message is None:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    prompt = update.message.text[3:].strip()
    
    if not prompt:
        await update.message.reply_text("Пожалуйста, введите описание после команды /ai")
        return

    chat_id = update.effective_chat.id
    logger.info(f"Команда: /ai, Пользователь: {user.full_name} (@{user.username or 'N/A'}), ID: {user.id}, Время: {time.strftime('%Y-%m-%d %H:%M:%S')}, Контекст: {prompt}")
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="⏳")

    try:
        ans = await gen_mesage_hug(prompt)
        await loading_msg.delete()
        #<song>
        if '</song>' == ans[-7:]:
            first = ans.rfind('<song>')
            title = ans[first+6:-7]
            print(title)
            context.args = [title]
            try:
                await send_track(update, context)
            except:
                print("ошибка отправки трека")
            ans = ans[:first]
        logger.info(f"Команда: /ai, Пользователь: {user.full_name} (@{user.username or 'N/A'}), ID: {user.id}, Время: {time.strftime('%Y-%m-%d %H:%M:%S')}, Контекст: {ans}")
        await update.message.reply_html(ans)
    except Exception as e:
        logger.error("Ошибка при генерации ответа", exc_info=True)
        await context.bot.send_message(chat_id=chat_id, text=f"Произошла ошибка: {str(e)}")

from router_models import get_models

async def ask_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
                global MODEL_ID
                MODEL_ID = models[type-1][0]
                await update.message.reply_text(f"Текущая модель: {models[type-1][1]}")
            else:
                await update.message.reply_text(f"❌ Номер моедли должен быть от 1 до {num}")
        except:
            await update.message.reply_text(f"❌ Номер модели должен быть числом")

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global context_messages 
    context_messages.clear()

#from yandex_music import Client

YA_TOKEN = os.getenv("YA_TOKEN")

from ya_down import *

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
        x = 3
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
                x-=1
                print("ERROR")
                logger.error(f"Ошибка при отправке аудио: {e}")
        await delayed_remove(err[0])
    else:
        await update.message.reply_text("❌ Трек не найден.")
    await loading_msg.delete()

#jokes

from jokes import get_random_cached_joke, initialize_caches

num = 0

async def send_random_joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global num
    logger.info(f"Получена команда /joke от {update.effective_user.full_name}")
    joke = await get_random_cached_joke(num)
    await update.message.reply_text(joke)
    num = (num%10)+1


def main():
    asyncio.run(initialize_caches())
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).read_timeout(60).write_timeout(60).connect_timeout(60).pool_timeout(60).build()
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("Hi", hi))
    app.add_handler(CommandHandler("ai", generate))
    app.add_handler(CommandHandler("mod", ask_models))
    app.add_handler(CommandHandler("music", send_track))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("joke", send_random_joke))

    app.add_error_handler(error_handler)

    app.run_polling()


if __name__ == '__main__':
    main()