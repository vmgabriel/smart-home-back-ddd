from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.enviroment_variable import model as adapter_model, dotenv_python as dotenv


class EnviromentVariableAdapter(enum.StrEnum):
    DOTENV = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> EnviromentVariableAdapter | None:
        try:
            return EnviromentVariableAdapter[type.upper()]
        except Exception:
            return None


ports: Dict[EnviromentVariableAdapter, Type[adapter_model.EnviromentVariableAdapter]] = {
    EnviromentVariableAdapter.DOTENV: dotenv.DotEnvPort,
    EnviromentVariableAdapter.FAKE: dotenv.DotEnvPort,
}

def get(port: str) -> Type[adapter_model.EnviromentVariableAdapter] | None:
    if selected_adapter := EnviromentVariableAdapter.get(port):
        return ports.get(selected_adapter)
    return None