from bot import main
from flask import Flask, request
from telegram.ext import Application
import os
import requests

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json(force=True)
    # Здесь нужна логика обработки webhook для python-telegram-bot
    return "OK"

def set_webhook():
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook'
    params = {
        'url': f'https://ваш-домен.repl.co/{TELEGRAM_BOT_TOKEN}'
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == '__main__':
    set_webhook()
    app.run(host='0.0.0.0', port=8080)