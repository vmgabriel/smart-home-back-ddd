from typing import Any, List

import json
import datetime

from app.security import domain
from app.adapter.uow import model, generics
from app.adapter.uow.psycopg import generics as psycopg_generics


USER_TABLE_NAME = "public.profile"
USER_FIELDS: List[str] = [
    "id",
    "email",
    "phone",
    "icon_url",
    "created_at",
    "updated_at",
    "deleted_at",
    "actived",
]


class ProfileCreatorPsycopgRepository(domain.ProfileCreatorRepository, psycopg_generics.PsycopgCRUDGenericRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(
            *args, 
            **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )



class ProfileGetterPsycopgRepository(domain.ProfileFinderRepository, psycopg_generics.PsycopgFinderRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(
            *args, **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )

    def serialize(self, data: Any) -> domain.Profile:
        return domain.Profile(
            id=str(data[0]),
            actived=bool(data[1]),
            created_at=data[2],
            updated_at=data[3],
            deleted_at=data[4],
            email=str(data[5]),
            phone=str(data[6]),
            icon_url=str(data[7]),
        )
