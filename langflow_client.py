import os
import json
import logging
import requests
from typing import Optional
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Константы из .env
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "cecec729-5bf1-4e50-b9c3-f9d55030a89e"
FLOW_ID = "b18386ad-c0be-49b6-b609-6004d56aa1b2"
APPLICATION_TOKEN = os.getenv('APPLICATION_TOKEN')

def run_flow(message: str, 
             endpoint: str = FLOW_ID, 
             output_type: str = "chat",
             input_type: str = "chat", 
             tweaks: Optional[dict] = None) -> dict:
    """
    Выполнение потока Langflow с заданным сообщением.
    
    :param message: Сообщение для отправки в поток
    :param endpoint: ID или имя endpoint потока
    :param tweaks: Опциональные настройки для кастомизации потока
    :return: JSON-ответ от потока
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    
    # Логирование параметров запроса
    logger.debug(f"API URL: {api_url}")
    logger.debug(f"Message: {message}")
    logger.debug(f"Application Token: {'*' * len(APPLICATION_TOKEN) if APPLICATION_TOKEN else 'Not set'}")

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }

    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        
        # Логирование полного ответа для отладки
        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Headers: {response.headers}")
        logger.debug(f"Response Content: {response.text}")

        response.raise_for_status()  # Вызовет исключение для плохих HTTP-статусов
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON: {e}")
        raise

def safe_get(obj, *keys, default=''):
    """
    Безопасное получение значения из вложенных словарей и списков
    с расширенной логикой поиска.
    
    :param obj: Исходный объект
    :param keys: Цепочка ключей для доступа
    :param default: Значение по умолчанию
    :return: Значение или default
    """
    try:
        for key in keys:
            if isinstance(obj, dict):
                obj = obj.get(key, {})
            elif isinstance(obj, list):
                # Если ключ - число и список не пустой
                if isinstance(key, int) and 0 <= key < len(obj):
                    obj = obj[key]
                else:
                    # Попытка найти первый элемент, если ключ не число
                    obj = obj[0] if obj else {}
            else:
                return default

        # Финальная проверка и извлечение текста
        if isinstance(obj, dict):
            # Пытаемся найти текстовое значение в словаре
            text_keys = ['message', 'text', 'content', 'value']
            for text_key in text_keys:
                if text_key in obj and isinstance(obj[text_key], str):
                    return obj[text_key]
        
        # Возвращаем строковое представление, если это возможно
        return str(obj).strip() if obj else default

    except Exception as e:
        logger.warning(f"Ошибка в safe_get: {e}")
        return default

def get_langflow_response(message: str) -> str:
    """
    Получение ответа от Langflow с расширенной логикой извлечения текста.
    
    :param message: Входящее сообщение
    :return: Текстовый ответ или сообщение об ошибке
    """
    try:
        response = run_flow(message)
        
        def text_generator():
            """Генератор для эффективного поиска текста"""
            yield from [
                safe_get(response, 'outputs', 0, 'outputs', 0, 'results', 'message', 'text'),
                safe_get(response, 'outputs', 0, 'outputs', 0, 'results', 'text'),
                safe_get(response, 'outputs', 0, 'messages', 0, 'message'),
                safe_get(response, 'messages', 0, 'message'),
                safe_get(response, 'outputs', 0, 'results', 'message', 'data', 'text'),
                safe_get(response, 'outputs', 0, 'results', 'data', 'text'),
                safe_get(response, 'messages', 0, 'text'),
                safe_get(response, 'messages', 'text')
            ]
        
        # Быстрый поиск первого непустого текста
        for msg in text_generator():
            if msg and isinstance(msg, str):
                cleaned_msg = msg.strip()
                if len(cleaned_msg) > 3:
                    logger.info(f"Получен ответ: {cleaned_msg}")
                    return cleaned_msg
        
        # Глубокий поиск с оптимизацией
        def extract_text(obj):
            """Рекурсивный поиск текста с ограничением глубины"""
            if isinstance(obj, str) and len(obj.strip()) > 3:
                return obj.strip()
            
            if isinstance(obj, dict):
                for value in obj.values():
                    result = extract_text(value)
                    if result:
                        return result
            
            if isinstance(obj, list):
                for item in obj:
                    result = extract_text(item)
                    if result:
                        return result
            
            return None
        
        fallback_text = extract_text(response)
        if fallback_text:
            logger.info(f"Извлечен текст методом fallback: {fallback_text}")
            return fallback_text
        
        logger.warning(f"Не удалось извлечь текст. Полный ответ: {response}")
        return "Извините, не удалось получить ответ от ассистента"
    
    except requests.RequestException as req_err:
        logger.error(f"Сетевая ошибка при запросе: {req_err}")
        return "Проблемы с подключением к серверу"
    except ValueError as val_err:
        logger.error(f"Ошибка обработки данных: {val_err}")
        return "Ошибка при обработке ответа"
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении ответа: {e}")
        return "Произошла непредвиденная ошибка"