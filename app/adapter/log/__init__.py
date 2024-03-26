from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.log import model as adapter_model, logging


class LogAdapter(enum.StrEnum):
    LOGGING = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> LogAdapter | None:
        try:
            return LogAdapter[type.upper()]
        except Exception:
            return None
        
        
ports: Dict[LogAdapter, Type[adapter_model.LogAdapter]] = {
    LogAdapter.LOGGING: logging.LoggingAdapter,
    LogAdapter.FAKE: logging.LoggingAdapter,
}

def get(port: str) -> Type[adapter_model.LogAdapter] | None:
    if selected_adapter := LogAdapter.get(port):
        return ports.get(selected_adapter)
    return None