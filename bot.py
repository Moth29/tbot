import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import re

from langflow_client import get_langflow_response  # Импортируем функцию

# Остальной код без изменений...

async def handle_message(update: Update, context):
    """Обработка всех входящих сообщений"""
    # Получаем текст сообщения
    message_text = update.message.text
    
    try:
        # Используем get_langflow_response вместо text_generator
        response = get_langflow_response(message_text)
        
        # Отправка ответа
        await update.message.reply_text(response)
    
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Попробуйте позже.")