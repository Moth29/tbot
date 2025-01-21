from flask import Flask, request
import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

app = Flask(__name__)

# Импортируем функции из bot.py
from bot import start_command, help_command, handle_message

@app.route(f'/{os.getenv("TELEGRAM_BOT_TOKEN")}', methods=['POST'])
async def webhook():
    # Получаем данные от Telegram
    update_data = await request.get_json(force=True)
    
    # Создаем Application
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Регистрируем хендлеры
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Обработка update
    await application.process_update(update_data)
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)