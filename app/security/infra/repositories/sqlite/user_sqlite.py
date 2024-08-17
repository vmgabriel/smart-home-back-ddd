from typing import Any, List

from app.security import domain
from app.adapter.uow import model, generics
from app.adapter.uow.sqlite import generics as sqlite_generics


USER_TABLE_NAME = "user"
USER_FIELDS: List[str] = [
    "name",
    "last_name",
    "username",
    "password",
]


class UserCreatorSqliteRepository(domain.UserCreatorRepository, sqlite_generics.SqliteCRUDGenericRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super(domain.UserCreatorRepository, self).__init__(
            *args, 
            **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )
        super(sqlite_generics.SqliteCRUDGenericRepository, self).__init__(
            *args, 
            **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )


class UserGetterSqliteRepository(domain.UserFinderRepository, sqlite_generics.SqliteFinderRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super(domain.UserCreatorRepository, self).__init__(
            *args, **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )
        super(sqlite_generics.SqliteFinderRepository, self).__init__(
            *args, **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )

    def by_username(self, username: str) -> domain.User | None:
        script = "SELECT * FROM {table} WHERE {filters};"
        _IS_USERNAME_FILTER = generics.Filter(definition="username = ?")

        res = self._session.execute(
            script.format(
                table=user_table_name,
                filters=_IS_USERNAME_FILTER.apply(value=username).filter.definition
            ),
            tuple(to_filter.generate_values)
        )

        found = res.fetchone()
        
        if not found:
            raise None
        
        return self.serialize(found)

    def serialize(self, data: Any) -> domain.User:
        print(f"data {data}")
        return domain.User(**data)
