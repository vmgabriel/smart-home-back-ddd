from typing import Tuple

import sqlite3

from app.adapter.uow import model


class SQLitePersistence(model.Persistence):
    _session: sqlite3.Cursor
    _connection: sqlite3.Connection
    
    def commit(self) -> None:
        self._connection.commit()
    
    def rollback(self) -> None:
        self._connection.rollback()
        
    def flush(self) -> None:
        # There are not flush method for sqlite 3
        ...


class SQLiteUOW(model.UOW):
    con: sqlite3.Connection
    
    def __init__(
        self, 
        log: model.log_model.LogAdapter,
        settings: model.lib_models.settings.Setting,
        persistence_creator: model.PersistenceCreator,
    ) -> None:
        super().__init__(log=log, settings=settings, persistence_creator=persistence_creator)
        self.con = sqlite3.connect(settings.migration_db_name)
        
    def _open(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        self.log.info("Opening Session DB")
        return self.con, self.con.cursor()
    
    def _close(self, session: sqlite3.Cursor) -> None:
        session.close()
        self.log.info("Closed Session DB")
        
