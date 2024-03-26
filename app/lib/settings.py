from typing import Dict

import pydantic
import pathlib

from app.lib import model as lib_models 


_SUMMARY = "API Smart Home Backend"
_DESCRIPTION = """Smart Home
"""

class Setting(pydantic.BaseModel):
    mode: lib_models.EnvironmentType = lib_models.EnvironmentType.PROD
    debug_level: lib_models.DebugLevelType = lib_models.DebugLevelType.ERROR
    
    # Path Main
    app_path: pathlib.Path = pathlib.Path("app")
    
    # Providers
    http_provider: str = "fastapi"
    server_provider: str = "uvicorn"
    log_provider: str = "logging"
    
    # Meta Documentation
    title: str = "Smart Home Back"
    summary: str = _SUMMARY
    description: str = _DESCRIPTION
    version: str = "0.0.1"
    contact: Dict[str, str] = {
        "name": "Gabriel Vargas Monroy",
        "url": "https://vmgabriel.com",
        "email": "vmgabriel96@gmail.com",
    }
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8080
    
    @property
    def has_debug(self) -> bool:
        return self.debug_level is not lib_models.DebugLevelType.NONE
