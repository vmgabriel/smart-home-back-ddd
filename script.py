import os
import telebot
from telethon.sync import TelegramClient
import dotenv


dotenv.load_dotenv()


TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE_DEFAULT = os.getenv("TELEGRAM_PHONE_DEFAULT")

assert TELEGRAM_API_ID
assert TELEGRAM_API_HASH
assert TELEGRAM_PHONE_DEFAULT


def generate_session_telegram() -> None:
    client = TelegramClient(
        "session",
        TELEGRAM_API_ID, 
        TELEGRAM_API_HASH,
    )
    client.connect()
    if not client.is_user_authorized():
        client.send_code_request(TELEGRAM_PHONE_DEFAULT)
        client.sign_in(TELEGRAM_PHONE_DEFAULT, input("Enter the code: "))
    else:
        print("Ya ha sido configurado")
    client.disconnect()


if __name__ == "__main__":
    generate_session_telegram()