from bot import main
from flask import Flask, request
import os
import telebot

app = Flask(__name__)
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

@app.route(f'/{os.getenv("TELEGRAM_BOT_TOKEN")}', methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK"

# Настройка webhook
bot.set_webhook(url=f'https://ваш-replit-домен.repl.co/{os.getenv("TELEGRAM_BOT_TOKEN")}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)