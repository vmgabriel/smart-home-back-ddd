import os

from app.lib import settings
from app.adapter import enviroment_variable as envvar

_ENV_PORT = os.getenv("ENV_PORT") or "DOTENV"


data = envvar.get(_ENV_PORT)()
SETTINGS = settings.Setting(**data.all())