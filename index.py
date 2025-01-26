import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Добавляем путь к родительской директории
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import start_command, help_command, handle_message

def handler(event, context):
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Создаем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем хендлеры
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработка update
    body = json.loads(event.get('body', '{}'))
    update = Update.de_json(body, application.bot)
    application.process_update(update)
    
    return {
        'statusCode': 200,
        'body': json.dumps({"status": "ok"})
    }