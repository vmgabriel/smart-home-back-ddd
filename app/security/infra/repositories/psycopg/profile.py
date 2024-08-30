from typing import Any, List

import json
import datetime

from app.security import domain
from app.adapter.uow import model, generics
from app.adapter.uow.psycopg import generics as psycopg_generics


USER_TABLE_NAME = "public.profile"
USER_FIELDS: List[str] = [
    "email",
    "phone",
    "icon_url",
    "created_at",
    "updated_at",
    "deleted_at",
    "actived",
]


class ProfileGetterPsycopgRepository(domain.ProfileFinderRepository, psycopg_generics.PsycopgFinderRepository):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(
            *args, **kwargs, 
            table_name=USER_TABLE_NAME, 
            fields=USER_FIELDS
        )

    def serialize(self, data: Any) -> domain.Profile:
        print(f"profile data {data}")
        return domain.User(
            id=str(data[0]),
            email=str(data[1]),
            phone=str(data[2]),
            icon_url=str(data[3]),
            actived=bool(data[4]),
            created_at=data[5],
            updated_at=data[6],
            deleted_at=data[7],
        )
