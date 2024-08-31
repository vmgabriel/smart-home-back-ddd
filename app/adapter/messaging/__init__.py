from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.messaging import model as adapter_model, telegram_telephone


class MessagingAdapter(enum.StrEnum):
    TELEGRAM_TELEPHONE = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> MessagingAdapter | None:
        try:
            return MessagingAdapter[type.upper()]
        except Exception:
            return None
        
        
ports: Dict[MessagingAdapter, Type[adapter_model.Messaging]] = {
    MessagingAdapter.TELEGRAM_TELEPHONE: telegram_telephone.TelegramTelephoneMessaging,
    MessagingAdapter.FAKE: telegram_telephone.TelegramTelephoneMessaging,
}

def get(port: str) -> Type[adapter_model.Messaging] | None:
    if selected_adapter := MessagingAdapter.get(port):
        return ports.get(selected_adapter)
    return None