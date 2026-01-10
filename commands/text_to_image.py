import asyncio
import json
import aiohttp
import requests


async def get_models_img():
    """Получение списка доступных моделей"""
    url = "https://subnp.com/api/free/models"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('success'):
                    return data.get('models', [])
                else:
                    print("API returned failure status")
                    return []
            else:
                print(f"Failed to fetch models: {response.status}")
                return []
     
async def generate_image(prompt, model = "wan"):
    """Генерация изображения"""
    base_url = "https://subnp.com"
    url = f"{base_url}/api/free/generate"
    
    payload = {
        "prompt": prompt,
        "model": model
    }
    
    headers = {"Content-Type": "application/json"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                async for line_bytes in response.content:
                    line = line_bytes.decode('utf-8').strip()
                    if line.startswith('data: '):
                        try:
                            # Убираем 'data: ' и парсим JSON
                            data = json.loads(line[6:])
                            print(line)
                            
                            status = data.get('status')
                            if status == 'processing':
                                print('Progress:', data.get('message'))
                            elif status == 'complete':
                                print('Image URL:', data.get('imageUrl'))
                            elif status == 'error':
                                print('Error:', data.get('message'))
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"Request failed with status {response.status}")
    return (status , data)

def simple_download_image(image_url, output_filename):
    """Простое скачивание изображения по URL"""
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Вызовет исключение при HTTP ошибках
        
        with open(output_filename, 'wb') as file:
            file.write(response.content)
        
        print(f"Image saved as {output_filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False

if __name__ == "__main__":
    print("Fetching available models...")
    models = asyncio.run(get_models_img())
    print("\nДоступные модели:")
    for i, model_info in enumerate(models, 1):
        print(f"{i}. Model: {model_info['model']}, Provider: {model_info['provider']}")
    print(models)
    if models:
        # Пример использования модели
        model = models[3]['model']
        print(f"\nGenerating image with model '{model}'...")
        #status, data = asyncio.create_task(generate_image("lamborgini miura in snowy forest, The car is moving and the snow is flying out from under the wheels", model))
        #if status == "complete":
        #    simple_download_image(data.get('imageUrl'), "image.jpg")