import abc

from app import lib as lib_models
from app.lib import model


class LogAdapter(abc.ABC):
    settings: lib_models.settings.Setting
    
    def __init__(self, settings: lib_models.settings.Setting) -> None:
        self.settings = settings
        
    def critical(self, msg: str) -> None:
        return self._message(msg=msg, status=model.DebugLevelType.CRITICAL)
        
    def info(self, msg: str) -> None:
        return self._message(msg=msg, status=model.DebugLevelType.INFO)
    
    def warning(self, msg: str) -> None:
        return self._message(msg=msg, status=model.DebugLevelType.WARNING)
    
    def error(self, msg: str) -> None:
        return self._message(msg=msg, status=model.DebugLevelType.ERROR)
    
    @abc.abstractmethod
    def _message(self, msg: str, status: model.DebugLevelType) -> None:
        raise NotImplemented