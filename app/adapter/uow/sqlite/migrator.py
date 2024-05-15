import sqlite4

from app import lib as lib_models
from app.adapter.uow import model
from app.adapter.log import model as log_model



_EXISTS_TABLE_BASE = """
SELECT name FROM sqlite_master WHERE type='table' AND name='migration';
"""


class SqliteMigration(model.Migration):
    db: sqlite4.SQLite4
    
    def __init__(self, log: log_model.LogAdapter, settings: lib_models.settings.Setting) -> None:
        super().__init__(log=log, settings=settings)
        self.db = sqlite4.SQLite4(settings.migration_db_name)
    
    def _is_migrated(self, migrator: model.MigrateContext) -> bool:
        self.db.connect()
        executed = self.db.execute(_EXISTS_TABLE_BASE)
        self.log.info(f"Executed data {executed}")
        return True
    
    def _mark_migrated(self) -> None:
        return
    
    def _rollback_unique(self, to_migrate: model.MigrateContext) -> None:
        return
    
    def _migrate_unique(self, to_migrate: model.Migrator) -> None:
        return