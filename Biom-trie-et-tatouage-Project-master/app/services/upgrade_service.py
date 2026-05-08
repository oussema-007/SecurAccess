# =============================================================================
# services/upgrade_service.py
# Service de gestion des demandes d'évolution de rôles (version mockée)
# =============================================================================

from typing import List
from datetime import datetime
from app.models.user import User, Role
from app.models.upgrade_request import UpgradeRequest, UpgradeStatus


class UpgradeService:
    """
    Gère les demandes d'évolution de compte (ex: USER vers PRO).
    Version mockée en mémoire, prête à être connectée à SQLite.
    """

    def __init__(self):
        self._requests: List[UpgradeRequest] = []
        self._next_id = 1

    def submit_upgrade_request(self, user: User, requested_role: Role, feature: str) -> UpgradeRequest:
        """
        Soumet une nouvelle demande d'évolution.
        """
        request = UpgradeRequest(
            id=self._next_id,
            user=user,
            requested_role=requested_role,
            feature_requested=feature,
            status=UpgradeStatus.PENDING,
            submitted_at=datetime.now()
        )
        self._requests.append(request)
        self._next_id += 1
        return request

    def get_all_requests(self) -> List[UpgradeRequest]:
        """Retourne toutes les demandes d'évolution."""
        return sorted(self._requests, key=lambda r: r.submitted_at, reverse=True)
