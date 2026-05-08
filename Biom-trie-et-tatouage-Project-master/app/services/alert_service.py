from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from app.services.database_service import DatabaseService


@dataclass
class SecurityAlert:
    """Modele d'alerte de securite."""

    id: int
    level: str
    title: str
    message: str
    is_read: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class AlertService:
    """
    Service de gestion d'alertes.

    Les alertes sont stockees en SQLite et exposees au dashboard admin.
    """

    def __init__(self, database_service: DatabaseService):
        self._db = database_service

    def create_alert(self, level: str, title: str, message: str) -> SecurityAlert:
        """Cree une alerte persistante."""
        created_at = datetime.now().isoformat()
        alert_id = self._db.execute_returning_id(
            """
            INSERT INTO security_alerts(level, title, message, is_read, created_at)
            VALUES (?, ?, ?, 0, ?)
            """,
            (level, title, message, created_at),
        )
        return SecurityAlert(
            id=alert_id,
            level=level,
            title=title,
            message=message,
            is_read=False,
            timestamp=datetime.fromisoformat(created_at),
        )

    def get_recent_alerts(self, limit: int = 50) -> List[SecurityAlert]:
        """Retourne les alertes recentes."""
        rows = self._db.fetch_all(
            """
            SELECT id, level, title, message, is_read, created_at
            FROM security_alerts
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [
            SecurityAlert(
                id=int(r["id"]),
                level=r["level"],
                title=r["title"],
                message=r["message"],
                is_read=bool(r["is_read"]),
                timestamp=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def get_counts(self) -> dict:
        """Retourne les compteurs par niveau."""
        rows = self._db.fetch_all(
            "SELECT level, COUNT(*) AS total FROM security_alerts GROUP BY level"
        )
        counts = {"critical": 0, "warning": 0, "info": 0, "total": 0}
        for row in rows:
            level = row["level"]
            total = int(row["total"])
            if level in counts:
                counts[level] = total
            counts["total"] += total
        return counts
