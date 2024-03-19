import abc
import pydantic

from app import lib as lib_models


class AppHttp(pydantic.BaseModel):
    instance: object | None = None


class HttpAdapter(abc.ABC):
    @abc.abstractmethod
    def execute(self, settings: lib_models.settings.Setting) -> AppHttp:
        raise NotImplemented