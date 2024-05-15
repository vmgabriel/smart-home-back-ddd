from __future__ import annotations
from typing import Dict, Type
import enum

from app.adapter.log import model as adapter_model, logging
from app.adapter.uow import model as uow_model
from app.adapter.uow.sqlite import migrator


class MigrationAdapter(enum.StrEnum):
    SQLITE = enum.auto()
    FAKE = enum.auto()
    
    @staticmethod
    def get(type: str) -> uow_model.Migration | None:
        try:
            return MigrationAdapter[type.upper()]
        except Exception:
            return None
        
        
migration_ports: Dict[MigrationAdapter, Type[uow_model.Migration]] = {
    MigrationAdapter.SQLITE: migrator.SqliteMigration,
    MigrationAdapter.FAKE: migrator.SqliteMigration,
}

def migration_get(port: str) -> Type[uow_model.Migration] | None:
    if selected_adapter := MigrationAdapter.get(port):
        return migration_ports.get(selected_adapter)
    return None