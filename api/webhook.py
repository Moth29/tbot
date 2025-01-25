from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os

# Импорт функций из основного бота
from bot import start_command, help_command, handle_message

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

@app.route('/api/webhook', methods=['POST'])
def webhook():
    # Получаем данные от Telegram
    update_data = request.get_json(force=True)
    
    # Создаем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем хендлеры
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработка update
    update = Update.de_json(update_data, application.bot)
    application.process_update(update)
    
    return jsonify({"status": "ok"})

def handler(event, context):
    return webhook()