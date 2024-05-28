import sqlite3

from app.adapter.uow import model


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
        
    def _open(self) -> sqlite3.Cursor:
        self.log.info("Opening Session DB")
        return self.con.cursor()
    
    def _close(self, session: sqlite3.Cursor) -> None:
        session.close()
        self.log.info("Closed Session DB")