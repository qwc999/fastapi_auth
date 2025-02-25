import pika
import os
import requests
from app.config import settings

TELEGRAM_BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID
credentials = pika.PlainCredentials('admin', 'admin')

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    response = requests.post(url, json=payload)
    return response.json()

def callback(ch, method, properties, body):
    user_data = body.decode().split()
    print(user_data)
    message = f"Новый пользователь зарегистрирован: {user_data[0]} {user_data[1]}. Почта {user_data[2]}"
    send_telegram_message(message)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue='user_registration', durable=True)
    channel.basic_consume(queue='user_registration', on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()