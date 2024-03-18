import abc
from typing import Any, Dict


class EnviromentVariableAdapter(abc.ABC):
    
    @abc.abstractmethod
    def get(self, key: str) -> str | None:
        raise NotImplemented
    
    @abc.abstractmethod
    def all(self) -> Dict[str, Any]:
        raise NotImplemented