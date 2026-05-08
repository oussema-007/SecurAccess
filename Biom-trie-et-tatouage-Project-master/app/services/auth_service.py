# =============================================================================
# services/auth_service.py
# Service d'authentification par reconnaissance faciale (version mockée)
#
# POINT D'INTÉGRATION FUTURE :
#   Remplacer la fonction `recognize_face()` par le vrai appel OpenCV/scikit-learn.
#   La signature et le type de retour doivent rester identiques pour ne pas
#   casser le reste de l'application.
# =============================================================================

import time
from datetime import datetime

import numpy as np

from app.models.auth_result import AuthResult, AuthStatus
from app.models.user import Role, User
from app.services.database_service import DatabaseService
from app.services.face_biometric_service import FaceBiometricService


# ---------------------------------------------------------------------------
# Base de données fictive d'utilisateurs enregistrés dans le système.
# En production, ces données viennent de SQLite via DatabaseService.
# ---------------------------------------------------------------------------
ROLE_BY_KEY = {
    "admin": Role.ADMIN,
    "user": Role.USER,
    "pro": Role.PRO,
    "ultimate": Role.ULTIMATE,
    "unauthorized": Role.UNAUTHORIZED,
}


class AuthService:
    """
    Service d'authentification par reconnaissance faciale.

    Version actuelle : retourne des résultats simulés selon un identifiant textuel.
    Version future   : analyse une image/frame OpenCV et retourne un AuthResult réel.

    Usage :
        service = AuthService()
        result  = service.recognize_face("user_face")
        # ou en production :
        result  = service.recognize_face_from_frame(opencv_frame)
    """

    # Strategie anti-faux positifs:
    # - <= strict: autoriser
    # - <= review: faible confiance -> inconnu (rejeter proprement)
    # - > review: inconnu
    # Seuils adaptes aux embeddings ArcFace normalises (distance euclidienne).
    # Seuils plus stricts pour reduire fortement les faux positifs.
    STRICT_THRESHOLD = 0.75
    REVIEW_THRESHOLD = 0.90

    def __init__(self, database_service: DatabaseService):
        self._db = database_service
        self._biometric = FaceBiometricService(database_service)

    def authenticate(self, face_roi: np.ndarray) -> AuthResult:
        """
        Authentifie un visage a partir d'une ROI.

        Cette implementation est un mock intelligent et deterministe.
        Elle sera remplacee plus tard par la vraie reconnaissance faciale.
        """
        time.sleep(0.2)
        user, confidence, diagnostics = self._match_from_templates(face_roi)
        if user is None:
            return AuthResult(
                status=AuthStatus.UNKNOWN,
                confidence=confidence,
                message=self._build_matching_message(
                    base_message="Visage inconnu dans le systeme.",
                    diagnostics=diagnostics,
                ),
                authorization_state="UNKNOWN",
                timestamp=datetime.now(),
            )

        if user.role == Role.UNAUTHORIZED or not user.is_active:
            return self._build_user_result(
                status=AuthStatus.UNAUTHORIZED,
                user=user,
                confidence=confidence,
                message=self._build_matching_message(
                    base_message="Utilisateur reconnu mais non autorise.",
                    diagnostics=diagnostics,
                ),
                authorization_state="DENIED",
            )

        if user.role == Role.ADMIN:
            return self._build_user_result(
                status=AuthStatus.ADMIN,
                user=user,
                confidence=confidence,
                message=self._build_matching_message(
                    base_message="Administrateur reconnu.",
                    diagnostics=diagnostics,
                ),
                authorization_state="AUTHORIZED",
            )

        return self._build_user_result(
            status=AuthStatus.AUTHORIZED,
            user=user,
            confidence=confidence,
            message=self._build_matching_message(
                base_message="Utilisateur autorise reconnu.",
                diagnostics=diagnostics,
            ),
            authorization_state="AUTHORIZED",
        )

    def _match_from_templates(self, face_roi: np.ndarray) -> tuple:
        """
        Trouve le meilleur utilisateur via les templates en base.

        Retourne (User|None, confidence, diagnostics).
        """
        if face_roi is None or face_roi.size == 0:
            return None, 0.0, {
                "distance": None,
                "strict_threshold": self.STRICT_THRESHOLD,
                "review_threshold": self.REVIEW_THRESHOLD,
            }

        try:
            embedding = self._biometric.build_embedding(face_roi)
        except Exception as exc:
            # FORCE LOG TO FILE SO WE CAN DEBUG
            with open("arcface_error.log", "w", encoding="utf-8") as f:
                f.write(str(exc))
            return None, 0.0, {
                "distance": None,
                "strict_threshold": self.STRICT_THRESHOLD,
                "review_threshold": self.REVIEW_THRESHOLD,
                "error": f"ARC_FACE_ERROR: {exc}",
            }
        user_id, distance = self._biometric.find_best_user_match(embedding)
        if user_id is None:
            return None, 0.0, {
                "distance": None,
                "strict_threshold": self.STRICT_THRESHOLD,
                "review_threshold": self.REVIEW_THRESHOLD,
                "error": "AUCUN_TEMPLATE_EN_BASE",
            }

        # Conversion distance -> confiance [0,1]
        confidence = max(0.0, min(1.0, 1.0 - (distance / 2.0)))
        diagnostics = {
            "distance": round(distance, 4),
            "strict_threshold": self.STRICT_THRESHOLD,
            "review_threshold": self.REVIEW_THRESHOLD,
        }
        if distance <= self.STRICT_THRESHOLD:
            return self._get_user_by_id(user_id), confidence, diagnostics
        if distance <= self.REVIEW_THRESHOLD:
            return None, confidence, diagnostics
        return None, confidence, diagnostics

    def _build_matching_message(self, base_message: str, diagnostics: dict) -> str:
        """Construit un message detaille de matching pour les logs."""
        if diagnostics.get("distance") is None:
            base = (
                f"{base_message} | score_distance=NA | "
                f"seuil_strict={self.STRICT_THRESHOLD:.2f} | "
                f"seuil_review={self.REVIEW_THRESHOLD:.2f}"
            )
            if diagnostics.get("error"):
                return f"{base} | erreur={diagnostics['error']}"
            return base
        return (
            f"{base_message} | score_distance={diagnostics['distance']:.4f} | "
            f"seuil_strict={self.STRICT_THRESHOLD:.2f} | "
            f"seuil_review={self.REVIEW_THRESHOLD:.2f}"
        )

    def _build_user_result(
        self,
        status: AuthStatus,
        user: User,
        confidence: float,
        message: str,
        authorization_state: str,
    ) -> AuthResult:
        """Construit un AuthResult complet a partir d'un utilisateur."""
        return AuthResult(
            status=status,
            role=user.role,
            user_id=user.id,
            full_name=user.name,
            email=user.email,
            authorization_state=authorization_state,
            confidence=confidence,
            message=message,
            user=user,
            timestamp=datetime.now(),
        )

    def _get_user_by_face_id(self, face_id: str) -> User:
        """Recupere un utilisateur depuis SQLite par face_id."""
        row = self._db.fetch_one(
            """
            SELECT id, face_id, full_name, email, role, is_active
            FROM users
            WHERE face_id = ?
            """,
            (face_id,),
        )
        if not row:
            return None

        role = ROLE_BY_KEY.get(row["role"], Role.UNKNOWN)
        return User(
            id=int(row["id"]),
            name=row["full_name"],
            email=row["email"],
            role=role,
            face_id=row["face_id"],
            is_active=bool(row["is_active"]),
        )

    def _get_user_by_id(self, user_id: int) -> User:
        """Recupere un utilisateur depuis SQLite par id."""
        row = self._db.fetch_one(
            """
            SELECT id, face_id, full_name, email, role, is_active
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        )
        if not row:
            return None
        role = ROLE_BY_KEY.get(row["role"], Role.UNKNOWN)
        return User(
            id=int(row["id"]),
            name=row["full_name"],
            email=row["email"],
            role=role,
            face_id=row["face_id"],
            is_active=bool(row["is_active"]),
        )
