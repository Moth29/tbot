from flask import Flask, request, jsonify
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import asyncio

app = Flask(__name__)

# Импортируем функции из bot.py
from bot import start_command, help_command, handle_message

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = 'https://28598463-5ae0-4197-b7c8-1c2d09c4360e-00-20esw1zptc3g5.kirk.replit.dev'

@app.route('/', methods=['GET'])
def index():
    return "Бот работает!", 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    # URL для установки webhook
    webhook_url = f'{WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}'
    
    # Отправляем запрос к Telegram API для установки webhook
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook'
    params = {
        'url': webhook_url
    }
    
    response = requests.get(url, params=params)
    return jsonify(response.json())

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
async def webhook():
    # Получаем данные от Telegram
    update_data = request.get_json(force=True)
    
    # Создаем Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Инициализируем Application
    await application.initialize()
    
    # Регистрируем хендлеры
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Создаем Update объект
    update = Update.de_json(update_data, application.bot)
    
    # Обработка update
    await application.process_update(update)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)