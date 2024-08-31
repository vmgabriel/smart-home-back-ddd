from typing import Dict, List

import pydantic
import pathlib
import datetime

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
    
    migration_provider: str = "psycopg"
    route_path_migrations: str = "app/adapter/uow/sqlite/migrations"
    migration_db_name: str = "temporal.db"
    enviroment_variables_provider: str = "dotenv"
    
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
    port: int = 3030
    
    # Domains
    domains: List[str] = [
        "security",
    ]

    # Security and Auth
    jwt_provider: str = "pyjwt"
    auth_type: str = "Bearer"
    authorization_name_attribute: str = "Authorization"
    expiration_access_token: datetime.timedelta = datetime.timedelta(hours=2)
    expiration_refresh_token: datetime.timedelta = datetime.timedelta(days=2)
    auth_access_token_secret: str = ""
    auth_refresh_token_secret: str = ""

    # Postgres Data
    postgres_port: str = "5432"
    postgres_dbname: str = ""
    postgres_host: str = ""
    postgres_username: str = ""
    postgres_password: str = ""

    messaging_provider: str = "telegram_telephone"

    # Telegram
    telegram_phone_default: str = ""
    telegram_api_hash: str = ""
    telegram_api_id: str = ""
    
    @property
    def has_debug(self) -> bool:
        return self.debug_level is not lib_models.DebugLevelType.NONE
