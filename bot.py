from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

# Токен и webhook
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
VERCEL_WEBHOOK_URL = 'https://tbot-snowy.vercel.app/api/webhook'

async def setup_webhook(application: Application):
    try:
        await application.bot.set_webhook(url=VERCEL_WEBHOOK_URL)
        logging.info(f"Webhook установлен на {VERCEL_WEBHOOK_URL}")
    except Exception as e:
        logging.error(f"Ошибка установки webhook: {e}")

async def start_command(update: Update, context):
    await update.message.reply_text('Привет! Я бот.')

async def help_command(update: Update, context):
    await update.message.reply_text('Чем могу помочь?')

async def handle_message(update: Update, context):
    text = update.message.text
    await update.message.reply_text(f'Вы сказали: {text}')

async def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Установка webhook
    await setup_webhook(application)
    
    # Регистрация хендлеров
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())