from yandex_music import Client
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB, TDRC, TRCK, error as ID3Error
from mutagen.mp3 import MP3
import asyncio
import os

YA_TOKEN = "y0__xCgoanTAxje-AYgnc3ruBIdszBHxDlqCEmFDfA3U7-h_jmnFg"

async def delayed_remove(file_path):
    await asyncio.sleep(2)  # Ждем 2 секунды
    try:
        os.remove(f'{file_path}.mp3')
        os.remove(f'{file_path}.jpg')
    except FileNotFoundError:
        pass  # файл уже удален или не существует
    except Exception as e:
        print(f"Ошибка при удалении файла {file_path}: {e}")

async def get_track(track_name):
    if not track_name:
        return 1

    client = Client(YA_TOKEN).init()
    result = client.search(track_name, type_='track')

    if result.tracks and result.tracks.results:
        track = result.tracks.results[0]
        file_name = track.title

        # Скачиваем обложку и трек
        track.download_og_image(f'{file_name}.jpg')
        track.download(f'{file_name}.mp3')

        # Ждем, пока файл появится
        while not os.path.exists(f'{file_name}.mp3'):
            await asyncio.sleep(1)

        # Загружаем MP3 и ID3-теги
        audio = MP3(f'{file_name}.mp3', ID3=ID3)
        if audio.tags is None:
            audio.add_tags()

        # Извлекаем данные из Яндекс.Музыки
        artists = [artist.name for artist in track.artists]
        album_title = track.albums[0].title if track.albums else "Unknown Album"
        year = str(track.albums[0].year) if track.albums and track.albums[0].year else "Unknown Year"
        track_number = str(track.albums[0].track_position) if track.albums and track.albums[0].track_position else "1"

        # Добавляем теги
        audio.tags.add(TPE1(encoding=3, text=artists))  # Исполнитель
        audio.tags.add(TIT2(encoding=3, text=file_name))  # Название трека
        audio.tags.add(TALB(encoding=3, text=album_title))  # Альбом
        audio.tags.add(TDRC(encoding=3, text=year))  # Год
        audio.tags.add(TRCK(encoding=3, text=track_number))  # Номер трека

        # Добавляем обложку
        with open(f'{file_name}.jpg', 'rb') as img_file:
            cover_data = img_file.read()
        audio.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,  # Front Cover
                desc='Cover',
                data=cover_data
            )
        )

        audio.save()
        return [file_name,artists]
    else:
        return 2

if __name__ == '__main__':
    asyncio.run(get_track(input()))