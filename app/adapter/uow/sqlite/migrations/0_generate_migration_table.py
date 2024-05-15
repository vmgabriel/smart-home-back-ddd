from app.adapter.uow import model

_UP = """
CREATE TABLE IF NOT EXISTS migrations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name VARCHAR(100) NOT NULL,
    created_at DEFAULT (DATETIME('now')),
);
"""

_ROLLBACK = """
DROP TABLE IF EXISTS migrations;
"""

migration = model.Migrator(
    up = _UP,
    rollback = _ROLLBACK,
)