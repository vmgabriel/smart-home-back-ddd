import logging

from app.lib import model
from app.lib.settings import Setting
from app.adapter.log import model as log_model


class LoggingAdapter(log_model.LogAdapter):
    log: logging.Logger
    level = {
        model.DebugLevelType.CRITICAL: 10,
        model.DebugLevelType.ERROR: 20,
        model.DebugLevelType.WARNING: 30,
        model.DebugLevelType.INFO: 40,
        model.DebugLevelType.NONE: 50,
    }
    
    def __init__(self, settings: Setting) -> None:
        super().__init__(settings)
        self.log = logging.getLogger(settings.title)
        self.log.setLevel(self.level[settings.debug_level])
    
    def _message(self, msg: str, status: model.DebugLevelType) -> None:
        self.log._log(level=self.level[status], msg=msg, args=tuple())