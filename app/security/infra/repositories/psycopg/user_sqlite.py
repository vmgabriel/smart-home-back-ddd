from typing import Any, List

import json
import datetime

from app.security import domain
from app.adapter.uow import model, generics
from app.adapter.uow.psycopg import generics as psycopg_generics


USER_TABLE_NAME = "public.user"
USER_FIELDS: List[str] = [
    "name",
    "last_name",
    "username",
    "password",
    "created_at",
    "updated_at",
    "deleted_at",
    "permissions",
    "actived",
]


class UserCreatorPsycopgRepository(domain.UserCreatorRepository, psycopg_generics.PsycopgCRUDGenericRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(
            *args, 
            **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )


class UserGetterPsycopgRepository(domain.UserFinderRepository, psycopg_generics.PsycopgFinderRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(
            *args, **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )

    def by_username(self, username: str) -> domain.User | None:
        script = "SELECT * FROM {table} WHERE {filters};"
        _IS_USERNAME_FILTER = generics.Filter(definition="username = %s")
        used_filter = _IS_USERNAME_FILTER.apply(value=username)

        res = self._session.execute(
            script.format(
                table=USER_TABLE_NAME,
                filters=used_filter.filter.definition
            ),
            tuple(used_filter.generate_values())
        )

        found = res.fetchone()
        
        if not found:
            return None
        
        return self.serialize(found)

    def serialize(self, data: Any) -> domain.User:
        return domain.User(
            id=str(data[0]),
            actived=bool(data[1]),
            name=data[2],
            last_name=data[3],
            username=data[4],
            password=data[5],
            created_at=data[6],
            updated_at=data[7],
            deleted_at=data[8],
            permissions=data[9],
        )
