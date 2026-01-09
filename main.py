import logging
import asyncio
from telegram.ext import *
import os
from dotenv import load_dotenv

# Import command handlers from separate modules
from commands.help_cmd import help
from commands.hi_cmd import hi
from commands.ai_cmd import generate
from commands.model_cmd import ask_models, clear
from commands.music_cmd import send_track
from commands.joke_cmd import send_random_joke
from commands.error_handler import error_handler
from jokes import initialize_caches

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