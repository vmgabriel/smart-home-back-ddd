import datetime
import sqlite3

from app import lib as lib_models
from app.adapter.uow import model
from app.adapter.log import model as log_model



_EXISTS_TABLE_BASE = """
SELECT name FROM sqlite_master WHERE type='table' AND name='migration';
"""

_MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS migration(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

_FIND_MIGRATION = """
SELECT * from migration WHERE file_name=(?);
"""

_MARK_AS_MIGRATED = """
INSERT INTO migration(file_name, created_at) VALUES (?, ?);
"""


class SqliteMigration(model.Migration):
    con: sqlite3.Connection
    cur: sqlite3.Cursor
    
    def __init__(self, log: log_model.LogAdapter, settings: lib_models.settings.Setting) -> None:
        super().__init__(log=log, settings=settings)
        self.con = sqlite3.connect(settings.migration_db_name)
        
    
    def _is_migrated(self, to_migrate: model.MigrateContext) -> bool:
        if not sqlite3.complete_statement(to_migrate.migrator.up):
            raise Exception(f"Not Complete Statement or with errors {to_migrate.name}")
        executed = self.cur.execute(_FIND_MIGRATION, (to_migrate.name,))
        return executed.fetchone() is not None
    
    def _mark_migrated(self, to_migrate: model.MigrateContext) -> None:
        current_date = datetime.datetime.now().isoformat()
        self.cur.execute(_MARK_AS_MIGRATED, (to_migrate.name, current_date))
        self.con.commit()
    
    def _rollback_unique(self, to_migrate: model.MigrateContext) -> None:
        if not to_migrate.has_migrated:
            self.log.info(f"{to_migrate.name} No require rollback")
        if not sqlite3.complete_statement(to_migrate.migrator.rollback):
            raise Exception(f"{to_migrate.name} Rollback is not Valid")
        self.cur.execute(to_migrate.migrator.rollback)
    
    def _migrate_unique(self, to_migrate: model.MigrateContext) -> None:
        self.cur.execute(to_migrate.migrator.up)
        to_migrate.has_migrated = True
        
    def _open(self) -> None:
        self.log.info("Open DB")
        self.cur = self.con.cursor()
        executed = self.cur.execute(_EXISTS_TABLE_BASE)
        if executed.fetchone() is not None:
            self.log.info("Initial Migration already completed")
            return
        
        self.log.info("Require Initial Migration")
        self.cur.execute(_MIGRATION_TABLE)
            
        
    def _close(self) -> None:
        self.log.info("Closing DB")
        self.con.close()
        self.log.info("Closed DB")
