# =============================================================================
# models/auth_result.py
# Résultat retourné par le service d'authentification faciale
# =============================================================================

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from app.models.user import Role, User


class AuthStatus(Enum):
    """Statuts standardises du pipeline d'authentification faciale."""

    AUTHORIZED = "authorized"
    ADMIN = "admin"
    UNAUTHORIZED = "unauthorized"
    UNKNOWN = "unknown"
    NO_FACE = "no_face"
    MULTIPLE_FACES = "multiple_faces"
    CAMERA_ERROR = "camera_error"


@dataclass
class AuthResult:
    """
    Resultat standard du flux d'authentification.

    Le schema est pret pour la vraie reconnaissance, la base SQLite,
    les logs, le tatouage et les alertes.
    """

    status: AuthStatus
    role: Optional[Role] = None
    user_id: Optional[int] = None
    full_name: str = ""
    email: str = ""
    authorization_state: str = ""
    confidence: float = 0.0
    message: str = ""
    user: Optional[User] = None
    timestamp: datetime = field(default_factory=datetime.now)
    face_image: Optional[bytes] = None

    @property
    def is_success(self) -> bool:
        """Vrai si l'authentification autorise l'acces."""
        return self.status in (AuthStatus.AUTHORIZED, AuthStatus.ADMIN)
