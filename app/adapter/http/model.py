import abc
import pydantic
from typing import List, Callable, Dict

from app import lib as lib_models
from app.lib import domain


class AppHttp(pydantic.BaseModel):
    instance: object | None = None


class HttpAdapter(abc.ABC):
    routes: List[domain.EntrypointWeb]
    functions_commands: Dict[str, Callable] = pydantic.Field(default_factory=dict)
    
    def __init__(self) -> None:
        self.routes = []
        self.functions_commands = []
        
    def set_functions_commands(self, cmds: Dict[object, Callable]) -> None:
        self.functions_commands = {cmd.__name__: fn for cmd, fn in cmds.items()}
    
    def add_route(self, entrypoint: domain.EntrypointWeb) -> None:
        self.routes.append(entrypoint)
        
    @abc.abstractmethod
    def _to_route(self, app: object, route: domain.EntrypointWeb) -> None:
        raise NotImplemented
    
    @abc.abstractmethod
    def execute(self, settings: lib_models.settings.Setting) -> AppHttp:
        raise NotImplemented