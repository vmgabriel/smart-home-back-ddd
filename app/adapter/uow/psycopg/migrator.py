import datetime
import psycopg

from app import lib as lib_models
from app.adapter.uow import model
from app.adapter.log import model as log_model



_EXISTS_TABLE_BASE = """
SELECT * FROM information_schema.tables WHERE table_name='migration';
"""

_MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS migration(
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

_FIND_MIGRATION = """
SELECT * from migration WHERE file_name=(%s);
"""

_MARK_AS_MIGRATED = """
INSERT INTO migration(file_name, created_at) VALUES (%s, %s);
"""


class PsycopgMigration(model.Migration):
    con: psycopg.Connection
    cur: psycopg.Cursor
    
    def __init__(self, log: log_model.LogAdapter, settings: lib_models.settings.Setting) -> None:
        super().__init__(log=log, settings=settings)
        conn_data = "postgresql://{user}:{password}@{host}:{port}/{dbname}".format(
            dbname=self.settings.postgres_dbname, 
            user=self.settings.postgres_username, 
            password=self.settings.postgres_password,
            host=self.settings.postgres_host,
            port=self.settings.postgres_port,
        )
        print(conn_data)
        self.con = psycopg.connect(conninfo=conn_data)
        
    
    def _is_migrated(self, to_migrate: model.MigrateContext) -> bool:
        executed = self.cur.execute(_FIND_MIGRATION, (to_migrate.name,))
        return executed.fetchone() is not None
    
    def _mark_migrated(self, to_migrate: model.MigrateContext) -> None:
        current_date = datetime.datetime.now()
        self.cur.execute(_MARK_AS_MIGRATED, (to_migrate.name, current_date))
        self.con.commit()
        self.log.info("Mark Migrated Correctly")
    
    def _rollback_unique(self, to_migrate: model.MigrateContext) -> None:
        if not to_migrate.has_migrated:
            self.log.info(f"{to_migrate.name} No require rollback")
        self.cur.execute(to_migrate.migrator.rollback)
    
    def _migrate_unique(self, to_migrate: model.MigrateContext) -> None:
        print(f"up {to_migrate.migrator.up}")
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

    def _close(self, exc_type, exc_value, exc_tb) -> None:
        self.log.info("Closing DB")
        self.cur.close()
        self.con.close()
        self.log.info("Closed DB")
