import asyncio
import logging
from telegram import Bot
from config_loader import load_config

# Load config for bot credentials and chat_id
config = load_config()
BOT_TOKEN = config['telegram']['bot_token']
CHAT_ID = config['telegram']['chat_id']

async def send_alert_async(message: str, photo_path: str):
    bot = Bot(token=BOT_TOKEN)
    try:
        with open(photo_path, "rb") as photo:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo, caption=message)
    except Exception as e:
        logging.error("Failed to send Telegram alert: " + str(e))

def send_alert(message: str, photo_path: str):
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(send_alert_async(message, photo_path))
    finally:
        loop.close()

if __name__ == '__main__':
    send_alert("Test alert", "graph.png")