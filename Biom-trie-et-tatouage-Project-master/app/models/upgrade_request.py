# =============================================================================
# models/upgrade_request.py
# Modèle de données pour une demande d'évolution de compte (upgrade)
# =============================================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from app.models.user import User, Role


class UpgradeStatus(Enum):
    """Statut d'une demande d'évolution de compte."""
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class UpgradeRequest:
    """
    Représente une demande d'un utilisateur pour obtenir un rôle supérieur,
    déclenchée après avoir cliqué sur une fonctionnalité restreinte.
    """
    id: int
    user: User                         # L'utilisateur faisant la demande
    requested_role: Role               # Le rôle demandé (ex: PRO, ULTIMATE)
    feature_requested: str             # La fonctionnalité qui a déclenché la demande
    status: UpgradeStatus = UpgradeStatus.PENDING
    submitted_at: datetime = field(default_factory=datetime.now)

    @property
    def status_label(self) -> str:
        """Label lisible du statut."""
        labels = {
            UpgradeStatus.PENDING:  "En attente",
            UpgradeStatus.APPROVED: "Approuvée",
            UpgradeStatus.REJECTED: "Rejetée",
        }
        return labels.get(self.status, "Inconnu")
