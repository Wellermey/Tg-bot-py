import logging
import asyncio
import aiohttp
import json
import time
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import load_dotenv
import os
from shared_state import context_messages

load_dotenv()

logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")
API_URL = f"https://openrouter.ai/api/v1/chat/completions"

async def gen_mesage_hug(prompt):
    global context_messages
    if len(context_messages) > 5:
        context_messages = context_messages[-5:]
    context_str = "Старые сообщения:"+ '\n'.join(context_messages)
    context_messages.append(f"\nПользователь: {prompt}")
    context_str = context_str + f"\nНовое сообщение: {prompt}"
    from shared_state import get_model_id
    headers = {
        "Authorization": f"Bearer {API_TOKEN}", 
    }
    data = {
        "model": get_model_id(),
        "stream": False,
        "max_tokens": 1024,
        "messages": [
            {
            "role": "system",
            "content":"Ты - ассистент в Telegram-боте. Отвечай на вопросы пользователя. Форматируй свой ответ для Telegram в html. Можно использовать только такие теги b, i, code, s, u, pre language=\"\". Не используй таблицы. Если промпт на музыкальную тему можно прикрепить ровно один музыкальный трек с помощью тега (обязательно в конце ответа) <song> название трека и исполнитель </song>",
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
                        if 'ём' in bot_response:
                            clean_response = bot_response[bot_response.find('ём') + 8:].strip()
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
    global context_messages
    from shared_state import get_model_id
    print(get_model_id())
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
                from commands.music_cmd import send_track
                await send_track(update, context)
            except:
                print("ошибка отправки трека")
            ans = ans[:first]
        logger.info(f"Команда: /ai, Пользователь: {user.full_name} (@{user.username or 'N/A'}), ID: {user.id}, Время: {time.strftime('%Y-%m-%d %H:%M:%S')}, Контекст: {ans}")
        await update.message.reply_html(ans)
    except Exception as e:
        logger.error("Ошибка при генерации ответа", exc_info=True)
        await context.bot.send_message(chat_id=chat_id, text=f"Произошла ошибка: {str(e)}")