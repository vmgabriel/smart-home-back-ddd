from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.jwt import model as adapter_model, pyjwt


class JWTAdapter(enum.StrEnum):
    PYJWT = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> JWTAdapter | None:
        try:
            return JWTAdapter[type.upper()]
        except Exception:
            return None
        
        
ports: Dict[JWTAdapter, Type[adapter_model.AuthJWT]] = {
    JWTAdapter.PYJWT: pyjwt.AuthPyJWT,
    JWTAdapter.FAKE: pyjwt.AuthPyJWT,
}

def get(port: str) -> Type[adapter_model.AuthJWT] | None:
    if selected_adapter := JWTAdapter.get(port):
        return ports.get(selected_adapter)
    return None