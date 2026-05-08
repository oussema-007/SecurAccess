# =============================================================================
# core/session.py
# Gestion de la session utilisateur courante (singleton)
#
# Le pattern Singleton garantit qu'il n'existe qu'une seule session
# active dans toute l'application à la fois.
# =============================================================================

from typing import Optional
from app.models.user import User, Role


class Session:
    """
    Gère la session de l'utilisateur actuellement connecté.
    Accessible depuis n'importe quel module via Session.get_instance().
    """

    _instance: "Session" = None  # Instance unique (Singleton)

    def __init__(self):
        self._current_user: Optional[User] = None
        self._is_admin_mode: bool = False  # True si l'admin utilise le dashboard

    @classmethod
    def get_instance(cls) -> "Session":
        """Retourne l'instance unique de Session (crée si premier appel)."""
        if cls._instance is None:
            cls._instance = Session()
        return cls._instance

    def login(self, user: User, admin_mode: bool = False) -> None:
        """
        Ouvre une session pour l'utilisateur donné.

        Args:
            user       : L'utilisateur reconnu.
            admin_mode : True si l'admin accède au dashboard admin.
        """
        self._current_user = user
        self._is_admin_mode = admin_mode

    def logout(self) -> None:
        """Ferme la session et réinitialise tous les attributs."""
        self._current_user = None
        self._is_admin_mode = False

    @property
    def current_user(self) -> Optional[User]:
        """L'utilisateur connecté, ou None si pas de session active."""
        return self._current_user

    @property
    def is_logged_in(self) -> bool:
        """Vrai si une session est active."""
        return self._current_user is not None

    @property
    def is_admin_mode(self) -> bool:
        """Vrai si l'admin a choisi d'accéder au dashboard admin."""
        return self._is_admin_mode

    def has_role(self, role: Role) -> bool:
        """Vérifie si l'utilisateur connecté a exactement ce rôle."""
        return self._current_user is not None and self._current_user.role == role

    def has_role_at_least(self, role: Role) -> bool:
        """Vérifie si l'utilisateur a ce rôle ou un rôle supérieur."""
        return self._current_user is not None and \
               self._current_user.has_role_at_least(role)

    def can_access_section(self, required_role: Role) -> bool:
        """
        Vérifie si l'utilisateur connecté peut accéder à une section donnée.
        L'admin a accès à tout.
        """
        if not self._current_user:
            return False
        return self._current_user.has_role_at_least(required_role)
