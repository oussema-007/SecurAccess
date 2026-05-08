# =============================================================================
# services/enrollment_service.py
# Service de gestion des demandes d'inscription (version mockée)
#
# POINT D'INTÉGRATION FUTURE :
#   Remplacer les listes en mémoire par des appels à SQLite via DatabaseService.
# =============================================================================

from datetime import datetime
from typing import List, Optional
from app.models.enrollment_request import EnrollmentRequest, RequestStatus


class EnrollmentService:
    """
    Gère les demandes d'inscription soumises par les visages inconnus.
    La version mockée stocke les demandes en mémoire (list Python).
    La version réelle utilisera une table SQLite dédiée.
    """

    def __init__(self):
        # Stockage en mémoire pour la démo — remplacé par SQLite en production
        self._requests: List[EnrollmentRequest] = [
            # Données fictives pré-chargées pour la démo du dashboard
            EnrollmentRequest(
                id=1,
                name="Sophie Laurent",
                email="sophie.laurent@mail.com",
                note="Employée du service RH, besoin d'accès rapidement.",
                status=RequestStatus.PENDING,
                submitted_at=datetime(2026, 4, 10, 9, 15),
            ),
            EnrollmentRequest(
                id=2,
                name="Thomas Girard",
                email="t.girard@mail.com",
                note="",
                status=RequestStatus.APPROVED,
                submitted_at=datetime(2026, 4, 9, 14, 30),
                processed_at=datetime(2026, 4, 11, 10, 0),
                processed_by="Alice Martin",
            ),
            EnrollmentRequest(
                id=3,
                name="Youssef Amrani",
                email="y.amrani@mail.com",
                note="Prestataire externe, accès temporaire demandé.",
                status=RequestStatus.REJECTED,
                submitted_at=datetime(2026, 4, 8, 16, 45),
                processed_at=datetime(2026, 4, 9, 9, 0),
                processed_by="Alice Martin",
            ),
        ]
        self._next_id = 4  # Auto-incrément simulé

    def submit_request(self, name: str, email: str, note: str = "") -> EnrollmentRequest:
        """
        Soumet une nouvelle demande d'inscription.

        Args:
            name  : Nom complet du demandeur.
            email : Email de contact.
            note  : Remarque facultative.

        Returns:
            EnrollmentRequest : La demande créée.
        """
        request = EnrollmentRequest(
            id=self._next_id,
            name=name,
            email=email,
            note=note,
            status=RequestStatus.PENDING,
            submitted_at=datetime.now(),
        )
        self._requests.append(request)
        self._next_id += 1
        return request

    def get_all_requests(self) -> List[EnrollmentRequest]:
        """Retourne toutes les demandes d'inscription, triées par date décroissante."""
        return sorted(self._requests, key=lambda r: r.submitted_at, reverse=True)

    def get_pending_requests(self) -> List[EnrollmentRequest]:
        """Retourne uniquement les demandes en attente."""
        return [r for r in self._requests if r.status == RequestStatus.PENDING]

    def approve_request(self, request_id: int, admin_name: str) -> bool:
        """Approuve une demande d'inscription."""
        request = self._find_by_id(request_id)
        if request:
            request.status = RequestStatus.APPROVED
            request.processed_at = datetime.now()
            request.processed_by = admin_name
            return True
        return False

    def reject_request(self, request_id: int, admin_name: str) -> bool:
        """Rejette une demande d'inscription."""
        request = self._find_by_id(request_id)
        if request:
            request.status = RequestStatus.REJECTED
            request.processed_at = datetime.now()
            request.processed_by = admin_name
            return True
        return False

    def get_stats(self) -> dict:
        """Retourne les statistiques des demandes pour le dashboard."""
        return {
            "total":    len(self._requests),
            "pending":  sum(1 for r in self._requests if r.status == RequestStatus.PENDING),
            "approved": sum(1 for r in self._requests if r.status == RequestStatus.APPROVED),
            "rejected": sum(1 for r in self._requests if r.status == RequestStatus.REJECTED),
        }

    def _find_by_id(self, request_id: int) -> Optional[EnrollmentRequest]:
        """Recherche interne d'une demande par son ID."""
        return next((r for r in self._requests if r.id == request_id), None)
