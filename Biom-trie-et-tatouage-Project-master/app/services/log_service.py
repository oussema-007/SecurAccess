# =============================================================================
# services/log_service.py
# Service de gestion commun des logs d'accès et d'actions
# =============================================================================

from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.services.database_service import DatabaseService
from app.services.watermark_service import WatermarkService


@dataclass
class LogEntry:
    """
    Représente un enregistrement de log (accès ou action intra-app).
    """
    id: int
    user_name: str          # Nom de l'utilisateur ou "Inconnu"
    user_role: str          # Rôle au moment de l'action
    status: str             # "Autorisé", "Refusé", "Inconnu", ou le type d'événement
    timestamp: datetime
    confidence: float       # Score de la reconnaissance, ou 0.0 pour les actions standard
    watermark: str          # [Futur] HMAC
    integrity_ok: bool = True
    details: str = ""       # Ex: "Feature: Espace Ultimate - Requis: ULTIMATE"

    @property
    def status_color(self) -> str:
        """Couleurs selon les types d'événements existants et nouveaux."""
        colors = {
            "Autorisé":  "#2ecc71",
            "Refusé":    "#e74c3c",
            "Inconnu":   "#f39c12",
            "Admin":     "#3498db",
            "RESTRICTED_ACCESS": "#e3b341",    # Clic sur un bouton restreint
            "UPGRADE_REQUEST": "#8957e5",      # L'utilisateur a demandé un upgrade
        }
        return colors.get(self.status, "#95a5a6")


class LogService:
    """
    Service de gestion des logs d'accès.
    Version mockée.
    """

    def __init__(self, database_service: DatabaseService, watermark_service: WatermarkService):
        self._db = database_service
        self._watermark_service = watermark_service

    def add_log(self, user_name: str, user_role: str, status: str,
                confidence: float = 0.0, details: str = "") -> LogEntry:
        """Enregistre un nouveau log en SQLite avec tatouage HMAC."""
        timestamp = datetime.now()
        payload = "|".join([
            user_name,
            user_role,
            status,
            f"{confidence:.4f}",
            details,
            timestamp.isoformat(),
        ])
        payload_hash = self._watermark_service.build_payload_hash(payload)
        signature = self._watermark_service.sign_payload(payload)

        log_id = self._db.execute_returning_id(
            """
            INSERT INTO auth_logs(
                user_name, user_role, status, confidence, details,
                watermark, payload_hash, integrity_ok, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                user_name,
                user_role,
                status,
                float(confidence),
                details,
                signature,
                payload_hash,
                timestamp.isoformat(),
            ),
        )

        entry = LogEntry(
            id=log_id,
            user_name=user_name,
            user_role=user_role,
            status=status,
            timestamp=timestamp,
            confidence=confidence,
            watermark=signature,
            integrity_ok=True,
            details=details
        )
        return entry

    def add_action_log(self, user_name: str, user_role: str, action_type: str, details: str = "") -> LogEntry:
        """
        Enregistre un log d'action spécifique post-connexion
        ex: Clic sur fonctionnalité bloquée, demande d'évolution.
        """
        return self.add_log(
            user_name=user_name,
            user_role=user_role,
            status=action_type,
            confidence=0.0,
            details=details
        )

    def get_recent_logs(self, limit: int = 20) -> List[LogEntry]:
        rows = self._db.fetch_all(
            """
            SELECT id, user_name, user_role, status, confidence, details, watermark, integrity_ok, created_at
            FROM auth_logs
            ORDER BY datetime(created_at) DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [
            LogEntry(
                id=int(row["id"]),
                user_name=row["user_name"],
                user_role=row["user_role"],
                status=row["status"],
                timestamp=datetime.fromisoformat(row["created_at"]),
                confidence=float(row["confidence"]),
                watermark=row["watermark"],
                integrity_ok=bool(row["integrity_ok"]),
                details=row["details"],
            )
            for row in rows
        ]

    def get_stats(self) -> dict:
        logs = self.get_recent_logs(limit=10000)
        return {
            "total":    len(logs),
            "allowed":  sum(1 for l in logs if l.status in ("Autorisé", "Admin")),
            "denied":   sum(1 for l in logs if l.status == "Refusé"),
            "unknown":  sum(1 for l in logs if l.status == "Inconnu"),
        }

    def verify_all_integrity(self) -> List[dict]:
        results = []
        rows = self._db.fetch_all(
            """
            SELECT id, user_name, user_role, status, confidence, details, watermark, payload_hash, created_at
            FROM auth_logs
            ORDER BY datetime(created_at) DESC
            """
        )
        for row in rows:
            payload = "|".join([
                row["user_name"],
                row["user_role"],
                row["status"],
                f"{float(row['confidence']):.4f}",
                row["details"],
                row["created_at"],
            ])
            computed_hash = self._watermark_service.build_payload_hash(payload)
            hash_ok = computed_hash == row["payload_hash"]
            sign_ok = self._watermark_service.verify_signature(payload, row["watermark"])
            is_ok = hash_ok and sign_ok
            results.append({
                "log_id":    int(row["id"]),
                "timestamp": datetime.fromisoformat(row["created_at"]),
                "user":      row["user_name"],
                "status":    row["status"],
                "integrity": is_ok,
                "watermark": row["watermark"],
            })
            self._db.execute(
                "UPDATE auth_logs SET integrity_ok = ? WHERE id = ?",
                (1 if is_ok else 0, int(row["id"])),
            )
        return results
