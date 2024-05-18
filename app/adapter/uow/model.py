from typing import List

import abc
import pydantic

from app import lib as lib_models
from app.adapter.log import model as log_model



class MigrationFailedError(Exception):
    message = "Migration not completed"
    
    
class MigrationsNotCompletedError(Exception):
    message = "Migrations Not complated"


class Migrator(pydantic.BaseModel):
    up: str
    rollback: str
    
    
class MigrateContext(pydantic.BaseModel):
    name: str
    migrator: Migrator
    has_migrated: bool = False


class Migration(abc.ABC):
    migrations: List[MigrateContext]
    log : log_model.LogAdapter
    settings: lib_models.settings.Setting
    
    def __init__(self, log: log_model.LogAdapter, settings: lib_models.settings.Setting) -> None:
        self.migrations = []
        self.log = log
        self.settings = settings
        
    def add_migrator(self, migrator: MigrateContext) -> None:
        self.migrations.append(migrator)
        
    def migrate(self) -> None:
        with self:
            for to_migrate in self.migrations:
                if not self._is_migrated(to_migrate):
                    try:
                        self.log.info(f"Making Migration {to_migrate.name}")
                        self._migrate_unique(to_migrate)
                        self._mark_migrated(to_migrate)
                    except MigrationFailedError as exc:
                        self.log.error(f"Migration Error - {exc}")
                        self.log.warning(f"Making Rollback {to_migrate.name}")
                        self._rollback_unique(to_migrate)
                        raise MigrationsNotCompletedError(message=str(exc))
            if all(not migration.has_migrated for migration in self.migrations):
                self.log.info("Not Require Migrations")
                
    def __enter__(self) -> None:
        self._open()
        
    def __exit__(self, exc_type, exc_value, exc_tb):
        self._close()
                
    @abc.abstractmethod
    def _open(self) -> None:
        raise NotImplementedError()
        
    @abc.abstractmethod
    def _close(self) -> None:
        raise NotImplementedError()
            
    @abc.abstractmethod
    def _is_migrated(self, to_migrate: MigrateContext) -> bool:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _mark_migrated(sel, to_migrate: MigrateContext) -> None:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _rollback_unique(self, to_migrate: MigrateContext) -> None:
        raise NotImplementedError()
    
    @abc.abstractmethod
    def _migrate_unique(self, to_migrate: MigrateContext) -> None:
        raise NotImplementedError()


class UOW(abc.ABC):
    async def __enter__(self):
        ...
        
    async def __exit__(self):
        ...
    
    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError()