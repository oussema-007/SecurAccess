# =============================================================================
# models/enrollment_request.py
# Modèle de données pour une demande d'inscription (visage inconnu)
# =============================================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class RequestStatus(Enum):
    """Statut d'une demande d'enrôlement en attente de traitement par l'admin."""
    PENDING  = "pending"   # En attente de validation admin
    APPROVED = "approved"  # Approuvée — enrôlement effectué
    REJECTED = "rejected"  # Rejetée par l'admin


@dataclass
class EnrollmentRequest:
    """
    Représente une demande d'inscription soumise par un visage inconnu.
    L'admin peut consulter et traiter ces demandes depuis son dashboard.
    """
    id: int
    name: str                          # Nom fourni par le demandeur
    email: str                         # Email de contact
    note: str = ""                     # Remarque facultative
    status: RequestStatus = RequestStatus.PENDING
    submitted_at: datetime = field(default_factory=datetime.now)
    processed_at: datetime = None      # Date de traitement par l'admin
    processed_by: str = ""             # Nom de l'admin qui a traité

    @property
    def status_label(self) -> str:
        """Label lisible du statut."""
        labels = {
            RequestStatus.PENDING:  "En attente",
            RequestStatus.APPROVED: "Approuvée",
            RequestStatus.REJECTED: "Rejetée",
        }
        return labels.get(self.status, "Inconnu")

    @property
    def status_color(self) -> str:
        """Couleur CSS selon le statut."""
        colors = {
            RequestStatus.PENDING:  "#f39c12",
            RequestStatus.APPROVED: "#2ecc71",
            RequestStatus.REJECTED: "#e74c3c",
        }
        return colors.get(self.status, "#95a5a6")
