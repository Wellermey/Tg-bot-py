# jokes_cache_manager.py
import asyncio
import logging
import random
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Глобальные переменные для хранения анекдотов
jokes_cache_primary = []
jokes_cache_secondary = []

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

async def fetch_jokes_from_web():
    url = "https://www.anekdot.ru/random/anekdot/"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    # Поиск div'ов с классом 'topicbox' - это основной контейнер анекдота
                    joke_divs = soup.find_all('div', class_='topicbox')
                    jokes = []
                    for div in joke_divs:
                        # Внутри topicbox ищем div с классом 'text' - это сам анекдот
                        text_div = div.find('div', class_='text')
                        if text_div:
                            # Извлекаем текст и убираем лишние пробелы
                            joke_text = text_div.get_text(strip=True)
                            if joke_text:
                                jokes.append(joke_text)
                    logger.info(f"Получено {len(jokes)} анекдотов с сайта.")
                    return jokes
                else:
                    logger.error(f"Ошибка при получении страницы: {response.status}")
                    return []
    except Exception as e:
        logger.error(f"Исключение при получении анекдотов: {e}")
        return []

async def initialize_caches():
    """
    Инициализирует основной и резервный кеш при запуске.
    """
    global jokes_cache_primary, jokes_cache_secondary
    logger.info("Инициализация кеша анекдотов...")
    fetched_jokes = await fetch_jokes_from_web()
    # Делим полученные анекдоты пополам
    mid_point = len(fetched_jokes) // 2
    jokes_cache_primary = fetched_jokes[:mid_point]
    jokes_cache_secondary = fetched_jokes[mid_point:]
    logger.info(f"Кеши инициализированы. Первичный: {len(jokes_cache_primary)}, Вторичный: {len(jokes_cache_secondary)}")

async def refresh_secondary_cache():
    """
    Обновляет резервный кеш новыми анекдотами.
    """
    global jokes_cache_secondary
    logger.info("Обновление резервного кеша...")
    new_jokes = await fetch_jokes_from_web()
    jokes_cache_secondary = new_jokes
    logger.info(f"Резервный кеш обновлён. Новых анекдотов: {len(new_jokes)}")

async def swap_caches():
    """
    Меняет местами основной и резервный кеш.
    """
    global jokes_cache_primary, jokes_cache_secondary
    logger.info("Переключение кешей...")
    
    jokes_cache_primary, jokes_cache_secondary = jokes_cache_secondary, jokes_cache_primary
    logger.info(f"Кеши переключены. Новый основной: {len(jokes_cache_primary)}, Новый резервный: {len(jokes_cache_secondary)}")

async def get_random_cached_joke(num):
    """
    Возвращает случайный анекдот из текущего основного кеша.
    Если основной кеш пуст, пытается переключить кеши.
    """
    global jokes_cache_primary
    
    if num == 10:
        logger.info("Основной кеш пуст, пытаемся переключить...")
        if jokes_cache_secondary:
            await swap_caches()
            # После переключения запускаем обновление нового резервного кеша
            await refresh_secondary_cache()
        else:
            logger.warning("Оба кеша пусты, невозможно получить анекдот.")
            return "На данный момент анекдоты недоступны. Попробуйте позже."
        num = 0
    asyncio.sleep(1)
    if jokes_cache_primary:
        return jokes_cache_primary[num]
    else:
        return "На данный момент анекдоты недоступны. Попробуйте позже."
        
if __name__ == "__main__":
    print(asyncio.run(fetch_jokes_from_web()))
