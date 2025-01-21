import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import re

from langflow_client import get_langflow_response

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Токен бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start_command(update: Update, context):
    """Обработчик команды /start"""
    welcome_text = (
        "Здравствуйте! Меня зовут Софья, я администратор ресторана. \n\n"
        "Я помогу Вам:\n"
        "- Разобраться в меню\n"
        "- Отвечу на Ваши вопросы\n"
        "- Всегда готова уладить любую проблему\n"
        "- Предоставлю подробную информацию по ресторану\n\n"
        "Просто напишите мне!"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context):
    """Обработчик команды /help"""
    help_text = (
        "Доступные команды:\n"
        "/start - Начать общение\n"
        "/help - Показать справку\n\n"
        "Просто напишите мне сообщение, и я постараюсь помочь!"
    )
    await update.message.reply_text(help_text)

async def send_long_message(update: Update, response: str):
    """Отправка длинных сообщений с разбиением"""
    MAX_MESSAGE_LENGTH = 4096
    
    while response:
        # Отправляем первые MAX_MESSAGE_LENGTH символов
        await update.message.reply_text(response[:MAX_MESSAGE_LENGTH])
        response = response[MAX_MESSAGE_LENGTH:]

def clean_text(text: str) -> str:
    """
    Очищает текст от лишних пробелов после точек и запятых.
    
    :param text: Исходный текст
    :return: Очищенный текст
    """
    # Удаляем лишние пробелы после точек и запятых
    text = re.sub(r'([.,!?])(\s*)', r'\1 ', text)
    # Удаляем двойные пробелы
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

async def handle_message(update: Update, context):
    """Обработка всех входящих сообщений"""
    # Получаем текст сообщения
    message_text = update.message.text
    
    try:
        # Генерация ответа через LangFlow
        response = get_langflow_response.text_generator(message_text)
        
        # Очистка текста
        response = clean_text(response)
        
        # Отправка ответа
        await send_long_message(update, response)
    
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Извините, произошла ошибка. Попробуйте позже.")

def main():
    """Основная функция запуска бота"""
    # Создаем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем хендлеры
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()