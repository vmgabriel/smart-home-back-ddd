from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.http import model as adapter_model, fastapi


class HttpAdapter(enum.StrEnum):
    FASTAPI = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> HttpAdapter | None:
        try:
            return HttpAdapter[type.upper()]
        except Exception:
            return None
        
        
ports: Dict[HttpAdapter, Type[adapter_model.HttpAdapter]] = {
    HttpAdapter.FASTAPI: fastapi.FastApiAdapter,
    HttpAdapter.FAKE: fastapi.FastApiAdapter,
}

def get(port: str) -> Type[adapter_model.HttpAdapter] | None:
    if selected_adapter := HttpAdapter.get(port):
        return ports.get(selected_adapter)
    return None