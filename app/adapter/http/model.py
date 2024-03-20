import abc
import pydantic
from typing import List

from app import lib as lib_models
from app.lib import domain


class AppHttp(pydantic.BaseModel):
    instance: object | None = None


class HttpAdapter(abc.ABC):
    routes: List[domain.EntrypointWeb]
    
    def __init__(self) -> None:
        self.routes = []
    
    def add_route(self, entrypoint: domain.EntrypointWeb) -> None:
        self.routes.append(entrypoint)
        
    @abc.abstractmethod
    def _to_route(self, app: object, route: domain.EntrypointWeb) -> None:
        raise NotImplemented
    
    @abc.abstractmethod
    def execute(self, settings: lib_models.settings.Setting) -> AppHttp:
        raise NotImplemented