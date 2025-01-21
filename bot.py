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
        current_message = response[:MAX_MESSAGE_LENGTH]
        await update.message.reply_text(current_message)
        response = response[MAX_MESSAGE_LENGTH:]

def clean_text(text: str) -> str:
    """
    Очищает текст от лишних пробелов после точек и запятых.
    
    :param text: Исходный текст
    :return: Очищенный текст
    """
    # Удаляем двойные пробелы после точек и запятых
    text = re.sub(r'([.,?!…])  +', r'\1 ', text)
    
    # Дополнительно удаляем пробелы в начале и конце строк
    text = '\n'.join(line.strip() for line in text.split('\n'))
    
    return text

async def handle_message(update: Update, context):
    """Обработка всех входящих сообщений"""
    try:
        # Логируем входящее сообщение
        user = update.effective_user
        message_text = update.message.text
        logger.info(f"Получено сообщение от {user.first_name} (ID: {user.id}): '{message_text}'")
        
        # Показываем индикатор набора текста
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, 
            action='typing'
        )
        
        # Получаем ответ от Langflow
        response = get_langflow_response(message_text)
        
        # Очищаем текст от лишних пробелов
        response = clean_text(response)
        
        # Логируем полученный ответ
        logger.info(f"Сгенерирован ответ: {response}")
        
        # Отправляем ответ с обработкой длинных сообщений
        await send_long_message(update, response)
    
    except Exception as e:
        error_message = f"Произошла ошибка: {str(e)}"
        logger.exception(error_message)
        
        try:
            await update.message.reply_text(error_message)
        except Exception as reply_error:
            logger.error(f"Не удалось отправить сообщение об ошибке: {reply_error}")

def main():
    """Основная функция запуска бота"""
    # Проверяем наличие токена
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Токен Telegram бота не установлен!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()