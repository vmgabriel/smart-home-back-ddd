from app.adapter.uow import model


_MIGRATION_TABLE = """
CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

_ROLLBACK = """
"""


migration = model.Migrator(
    up=_MIGRATION_TABLE,
    rollback=_ROLLBACK,
)