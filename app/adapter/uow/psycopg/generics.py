from typing import List, cast, Any

import psycopg
import datetime

from app import lib as lib_models
from app.adapter.log import model as log_model
from app.adapter.uow import generics, model


_INSERT_DEFAULT = "INSERT INTO {} ({}) VALUES ({}) RETURNING id;"
_UPDATE_DEFAULT = "UPDATE {} SET {} WHERE {};"
_DELETE_DEFAULT = "UPDATE {} SET {} WHERE {};"  # It's the same, logic delete

_SELECT_DEFAULT = "SELECT * FROM {} WHERE {};"
_SELECT_WITH_OFFSET_LIMIT_DEFAULT = "SELECT * FROM {} WHERE {} LIMIT {},{};"
_IS_ID_FILTER = generics.Filter(definition="id = %s")
_IS_ACTIVED_FILTER = generics.Filter(definition="actived = %s")


class PsycopgCRUDGenericRepository(generics.UpdateGenericRepository):
    table_name: str
    fields: List[str]

    def __init__(
        self,
        *args: Any,
        table_name: str,
        fields: List[str],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.fields = fields

    def _fields(self, value: Any) -> str:
        return value
        # if value == None:
        #     return ""
        # match type(value):
        #     case datetime.datetime:
        #         return cast(datetime.datetime, value).isoformat()
        #     case _:
        #         return value
    
    def create(self, new: model.RepositoryData) -> model.RepositoryData:
        query = _INSERT_DEFAULT.format(
            self.table_name,
            ",".join(self.fields),
            ",".join(["%s" for _ in self.fields]),
        )
        fields = tuple(self._fields(getattr(new, x)) for x in self.fields)
        _LOG_PROVIDER.info(f"query {query}")
        result = self._session.execute(query, fields)
        new.id = str(next(result)[0])
        return new
            
    def update(self, id: Any, to_update: model.RepositoryData) -> model.RepositoryData:
        self._session.execute(
            _UPDATE_DEFAULT.format(
                self.table_name,
                ",".join([f"{field} = %s" for field in self.fields if field != "id"]),
                "id = %s"
            ),
            (*(getattr(to_update, field) for field in self.fields if field != "id"), id)
        )
        return to_update
        
    def delete(self, id: Any) -> None:
        self._session.execute(
            _DELETE_DEFAULT.format(self.table_name, _IS_ACTIVED_FILTER.definition, _IS_ID_FILTER.definition),
            (False, id)
        )
        
class PsycopgFinderRepository(generics.GetterGenericRepository):
    table_name: str
    fields: List[str]

    def __init__(
        self,
        *args: Any,
        table_name: str, 
        fields: List[str],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.table_name = table_name
        self.fields = fields
    
    def get_by_id(self, id: Any) -> model.RepositoryData:
        to_filter = _IS_ID_FILTER.apply(id)
        res = self._session.execute(
            _SELECT_DEFAULT.format(
                self.table_name,
                to_filter.filter.definition
            ),
            tuple(to_filter.generate_values())
        )
        found = res.fetchone()
        if not found:
            raise model.RepositoryNotFoundError()
        return self.serialize(found)
        
    def filter(self, filters: List[generics.ToFilter], page: int = 0, count: int = 20) -> generics.Filtered:
        script = _SELECT_WITH_OFFSET_LIMIT_DEFAULT.format(
            self.table_name, 
            f"{_IS_ACTIVED_FILTER.definition}" + "AND" if filters else "" + " AND ".join([filter.filter.definition for filter in filters]),
            page,
            count
        )
        inject = [values for filter in filters for values in filter.generate_values()]
        res = self._session.execute(script, tuple(inject))
        return [self.serialize(record) for record in res.fetchall()]