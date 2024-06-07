from typing import List, cast, Any

import sqlite3

from app import lib as lib_models
from app.adapter.log import model as log_model
from app.adapter.uow import generics, model


_INSERT_DEFAULT = "INSERT INTO {} ({}) VALUE ({});"
_UPDATE_DEFAULT = "UPDATE {} SET {} WHERE {};"
_DELETE_DEFAULT = "UPDATE {} SET {} WHERE {};"  # It's the same, logic delete

_SELECT_DEFAULT = "SELECT * FROM {} WHERE {};"
_SELECT_WITH_OFFSET_LIMIT_DEFAULT = "SELECT * FROM {} WHERE {} LIMIT {},{};"
_IS_ID_FILTER = generics.Filter(definition="id = ?")
_IS_ACTIVED_FILTER = generics.Filter(definition="actived = ?")


class SqliteCRUDGenericRepository(generics.CRUDGenericRepository):
    _session: sqlite3.Cursor
    settings: lib_models.settings.Setting
    log: log_model.LogAdapter
    table_name: str
    fields: List[str]
    
    def create(self, new: model.RepositoryData) -> model.RepositoryData:
        self._session.execute(
            _INSERT_DEFAULT.format(
                self.table_name,
                ",".join(self.fields),
                ",".join(["?" for _ in self.fields]),
            ),
            (getattr(new, x) for x in self.fields)
        )
        return new
            
    def update(self, id: Any, to_update: model.RepositoryData) -> model.RepositoryData:
        self._session.execute(
            _UPDATE_DEFAULT.format(
                self.table_name,
                ",".join([f"{field} = ?" for field in self.fields if field != "id"]),
                "id = ?"
            ),
            (*(getattr(to_update, field) for field in self.fields if field != "id"), id)
        )
        return to_update
        
    def delete(self, id: Any) -> None:
        self._session.execute(
            _DELETE_DEFAULT.format(self.table_name, _IS_ACTIVED_FILTER.definition, _IS_ID_FILTER.definition),
            (False, id)
        )
        
class SqliteFinderRepository(generics.GetterGenericRepository):
    _session: sqlite3.Cursor
    settings: lib_models.settings.Setting
    log: log_model.LogAdapter
    table_name: str
    fields: List[str]
    
    def get_by_id(self, id: Any) -> model.RepositoryData:
        to_filter = _IS_ID_FILTER.apply(id)
        res = self._session.execute(
            _SELECT_DEFAULT.format(
                self.table_name, 
                to_filter.filter.definition
            ),
            tuple(to_filter.generate_values)
        )
        found = res.fetchone()
        if not found:
            raise model.RepositoryNotFoundError()
        return self.serialize(found)
        
    def filter(self, filters: List[generics.ToFilter], page: int = 0, count: int = 20) -> model.Filtered:
        script = _SELECT_WITH_OFFSET_LIMIT_DEFAULT.format(
            self.table_name, 
            f"{_IS_ACTIVED_FILTER.definition}" + "and" if filters else "" + " and ".join([filter.filter.definition for filter in filters]),
            page,
            count
        )
        inject = [values for filter in filters for values in filter.generate_values()]
        res = self._session.execute(script, tuple(inject))
        return [self.serialize(record) for record in res.fetchall()]