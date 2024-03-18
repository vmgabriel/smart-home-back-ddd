from typing import Any, Dict
import dotenv

from app.adapter.enviroment_variable import model


class DotEnvPort(model.EnviromentVariableAdapter):
    obj: dotenv.DotEnv
    
    def __init__(self) -> None:
        super().__init__()
        self.obj = dotenv.DotEnv()
        
    def get(self, value: str) -> str | None:
        return self.obj.get(value=value)
    
    def all(self) -> Dict[str, Any]:
        return {k.lower(): v for k,v in self.obj.all().items()}