import abc

from app import lib as lib_models
from app.adapter.http import model as http_model


class ServerAdapter(abc.ABC):
    @abc.abstractmethod
    def execute(
        self, 
        port: http_model.AppHttp, 
        settings: lib_models.settings.Setting
    ) -> None:
        raise NotImplemented
