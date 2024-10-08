from typing import Any, Dict

import dotenv
import pathlib

from app.adapter.enviroment_variable import model


class DotEnvPort(model.EnviromentVariableAdapter):
    obj: dotenv.main.DotEnv
    
    def __init__(self) -> None:
        super().__init__()
        path = pathlib.Path() / ".env"
        dotenv.load_dotenv(dotenv_path=path.absolute())
        self.obj = dotenv.main.DotEnv(dotenv_path=path.absolute())
        
    def get(self, value: str) -> str | None:
        return self.obj.get(value=value)
    
    def all(self) -> Dict[str, Any]:
        return {k.lower(): v for k,v in self.obj.dict().items()}