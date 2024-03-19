from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.server import model as adapter_model, uvicorn


class ServerAdapter(enum.StrEnum):
    UVICORN = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> ServerAdapter | None:
        try:
            return ServerAdapter[type.upper()]
        except Exception:
            return None
        
        
ports: Dict[ServerAdapter, Type[adapter_model.ServerAdapter]] = {
    ServerAdapter.UVICORN: uvicorn.UvicornAdapter,
    ServerAdapter.FAKE: uvicorn.UvicornAdapter,
}

def get(port: str) -> Type[adapter_model.ServerAdapter] | None:
    if selected_adapter := ServerAdapter.get(port):
        return ports.get(selected_adapter)
    return None