from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.log import model as adapter_model, logging
from app.adapter.uow import model as uow_model
from app.adapter.uow.sqlite import migrator, uow as sqlite_uow
from app.adapter.uow.psycopg import migrator as psycopg_migrator, uow as psycopg_uow


class PersistencyAdapter(enum.StrEnum):
    SQLITE = enum.auto()
    PSYCOPG = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> uow_model.Migration | None:
        try:
            return PersistencyAdapter[type.upper()]
        except Exception:
            return None
        
        
migration_ports: Dict[PersistencyAdapter, Type[uow_model.Migration]] = {
    PersistencyAdapter.SQLITE: migrator.SqliteMigration,
    PersistencyAdapter.PSYCOPG: psycopg_migrator.PsycopgMigration,
    PersistencyAdapter.FAKE: migrator.SqliteMigration,
}

uow_port: Dict[PersistencyAdapter, Type[uow_model.UOW]] = {
    PersistencyAdapter.SQLITE: sqlite_uow.SQLiteUOW,
    PersistencyAdapter.PSYCOPG: psycopg_uow.PsycopgUOW,
    PersistencyAdapter.FAKE: sqlite_uow.SQLiteUOW,
}

persistence_ports:Dict[PersistencyAdapter, Type[uow_model.Persistence]] = {
    PersistencyAdapter.SQLITE: sqlite_uow.SQLitePersistence,
    PersistencyAdapter.PSYCOPG: psycopg_uow.PsycopgPersistence,
    PersistencyAdapter.FAKE: sqlite_uow.SQLitePersistence,
}

def migration_get(port: str) -> Type[uow_model.Migration] | None:
    if selected_adapter := PersistencyAdapter.get(port):
        return migration_ports.get(selected_adapter)
    return None


def uow_get(port: str) -> Type[uow_model.UOW] | None:
    if selected_adapter := PersistencyAdapter.get(port):
        return uow_port.get(selected_adapter)
    return None


def persistence_get(port: str) -> Type[uow_model.Persistence] | None:
    if selected_adapter := PersistencyAdapter.get(port):
        return persistence_ports.get(selected_adapter)
    return None