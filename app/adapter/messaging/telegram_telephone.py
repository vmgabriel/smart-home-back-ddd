import telebot
from telethon.sync import TelegramClient

from app.adapter.messaging import model
from app import lib as lib_models
from app.adapter.log import model as log_model


class TelegramTelephoneMessaging(model.Messaging):
    _client: TelegramClient

    def __init__(self, settings: lib_models.settings.Setting, log: log_model.LogAdapter) -> None:
        super().__init__(settings=settings, log=log)
        self._client = TelegramClient(
            "session",
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )

    def send(self, phone_destination: str, message: str) -> None:
        self._client.connect()
        self._client.send_message(phone_destination, message)
        self._client.disconnect()
