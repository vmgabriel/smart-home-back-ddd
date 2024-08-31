import abc

from app import lib as lib_models
from app.adapter.log import model as log_model


class Messaging(abc.ABC):
    settings: lib_models.settings.Setting
    log: log_model.LogAdapter

    def __init__(self, settings: lib_models.settings.Setting, log: log_model.LogAdapter) -> None:
        self.settings = settings
        self.log = log

    def send(self, phone_destination: str, message: str) -> None:
        raise NotImplementedError()

