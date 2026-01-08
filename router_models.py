import requests

url = "https://openrouter.ai/api/v1/models"
response = requests.get(url)

def get_models():
    # Проверка успешности запроса
    if response.status_code == 200:
        models_data = response.json()

        # Переменная для подсчета найденных "бесплатных" моделей
        free_model_count = 0
        models = []
        for model in models_data.get('data', []): # Используем .get() для безопасности
            pricing = model.get('pricing', {})
            prompt_price = pricing.get('prompt', 'N/A')
            
            # Проверяем, является ли цена за токены запроса "бесплатной" (0.0)
            # Используем float() для безопасного преобразования строки в число
            try:
                if float(prompt_price) == 0.0:
                    models.append((model.get('id', 'N/A'), model.get('name', 'N/A'), ))
                    free_model_count += 1
            except ValueError:
                # Если prompt_price не может быть преобразовано в float (например, 'N/A'), пропускаем
                continue

        return free_model_count, models
    else:
        return 0, []