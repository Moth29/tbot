# index.py
from api.webhook import handler

# Vercel требует точку входа
def main(event, context):
    return handler(event, context)