import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional


class DatabaseService:
    """
    Service d'acces SQLite centralise.

    Ce service gere la creation des tables et offre des helpers simples
    pour executer des requetes de lecture/ecriture.
    """

    def __init__(self, db_path: Optional[str] = None):
        data_dir = Path("data")
        data_dir.mkdir(parents=True, exist_ok=True)
        self._db_path = Path(db_path) if db_path else data_dir / "securaccess.db"
        self._initialize_schema()
        self._seed_users_if_needed()

    @property
    def db_path(self) -> str:
        return str(self._db_path)

    def _connect(self) -> sqlite3.Connection:
        """
        Ouvre une connexion SQLite robuste face aux verrous temporaires.
        """
        conn = sqlite3.connect(self._db_path, timeout=10.0)
        conn.execute("PRAGMA busy_timeout = 10000")
        return conn

    def execute(self, query: str, params: Iterable = ()) -> None:
        """Execute une requete d'ecriture."""
        with self._connect() as conn:
            conn.execute(query, tuple(params))
            conn.commit()

    def execute_returning_id(self, query: str, params: Iterable = ()) -> int:
        """Execute une insertion et retourne l'identifiant cree."""
        with self._connect() as conn:
            cur = conn.execute(query, tuple(params))
            conn.commit()
            return int(cur.lastrowid)

    def fetch_all(self, query: str, params: Iterable = ()) -> List[sqlite3.Row]:
        """Retourne toutes les lignes d'une requete."""
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(query, tuple(params))
            return cur.fetchall()

    def fetch_one(self, query: str, params: Iterable = ()) -> Optional[sqlite3.Row]:
        """Retourne une ligne ou None."""
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def _initialize_schema(self) -> None:
        """Cree les tables necessaires si elles n'existent pas."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    face_id TEXT NOT NULL UNIQUE,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_name TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0.0,
                    details TEXT NOT NULL DEFAULT '',
                    watermark TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    integrity_ok INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS face_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    embedding TEXT NOT NULL,
                    image_path TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.commit()

    def _seed_users_if_needed(self) -> None:
        """Insere des utilisateurs de demo pour l'auth faciale."""
        row = self.fetch_one("SELECT COUNT(*) AS total FROM users")
        if row and int(row["total"]) > 0:
            return

        demo_users = [
            ("admin_face", "Alice Martin", "alice.martin@securaccess.fr", "admin", 1),
            ("user_face", "Bob Dupont", "bob.dupont@securaccess.fr", "user", 1),
            ("pro_face", "Clara Benali", "clara.benali@securaccess.fr", "pro", 1),
            ("ultimate_face", "David Chen", "david.chen@securaccess.fr", "ultimate", 1),
            ("blocked_face", "Eric Moreau", "eric.moreau@securaccess.fr", "unauthorized", 0),
        ]
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO users(face_id, full_name, email, role, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                demo_users,
            )
            conn.commit()
