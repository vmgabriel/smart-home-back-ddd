from typing import List, Generator, Any

import pydantic
import abc

from app import lib as lib_models
from app.adapter.log import model as log_model
from app.adapter.uow import model


class Filtered(pydantic.BaseModel):
    total: int = pydantic.Field(default_factory=0)
    page: int = pydantic.Field(default_factory=0)
    count: int = pydantic.Field(default_factory=0)
    elements: List[model.RepositoryData] = pydantic.Field(default_factory=list)
    
    @property
    def total_pages(self) -> int:
        return self.total // self.count
        
    @property
    def has_previous(self) -> bool:
        return self.page in (0, 1)
        
    @property
    def has_next(self) -> bool:
        return self.total_pages < self.page
    


class CRUDGenericRepository(abc.ABC):
    _session: object
    settings: lib_models.settings.Setting
    log: log_model.LogAdapter
    
    def __init__(
        self,
        _session: object,
        log: log_model.LogAdapter, 
        settings: lib_models.settings.Setting,
    ) -> None:
        super().__init__()
        self.log = log
        self.settings = settings
        self._session = _session
        
    @abc.abstractmethod
    def create(self, new: model.RepositoryData) -> model.RepositoryData:
        raise NotImplementedError()
            
    @abc.abstractmethod    
    def update(self, id: Any, to_update: model.RepositoryData) -> model.RepositoryData:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def delete(self, id: Any) -> None:
        raise NotImplementedError()
        
        
class ToFilter(pydantic.BaseModel):
    filter: "Filter"
    value: Any
    
    def generate_values(self) -> Generator[None, Any, None]:
        for _ in range(self.filter.values):
            yield self.value


class Filter(pydantic.BaseModel):
    definition: str
    values: int = 1
    
    def apply(self, value: Any) -> ToFilter:
        return ToFilter(filter=filter, value=value)

        
class GetterGenericRepository(abc.ABC):
    _session: object
    settings: lib_models.settings.Setting
    log: log_model.LogAdapter,
    
    def __init__(
        self,
        _session: object,
        log: log_model.LogAdapter, 
        settings: lib_models.settings.Setting,
    ) -> None:
        super().__init__()
        self.log = log
        self.settings = settings
        self._session = _session
        
    @abc.abstractmethod
    def serialize(self, data: Any) -> model.RepositoryData:
        raise NotImplementedError
    
    @abc.abstractmethod
    @staticmethod
    def get_by_id(self, id: Any) -> model.RepositoryData:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def filter(self, filters: List[ToFilter], page: int = 1, count: int = 20) -> Filtered:
        raise NotImplementedError()