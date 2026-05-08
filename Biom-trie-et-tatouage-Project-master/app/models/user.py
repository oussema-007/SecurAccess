# =============================================================================
# models/user.py
# Modèle de données pour un Utilisateur du système
# =============================================================================

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class Role(Enum):
    """
    Enumération des rôles disponibles dans le système.
    Chaque rôle détermine les sections accessibles dans l'application.
    """
    ADMIN       = "admin"        # Accès total, peut gérer le système
    ULTIMATE    = "ultimate"     # Accès à toutes les sections utilisateur
    PRO         = "pro"          # Accès aux sections pro + user
    USER        = "user"         # Accès aux sections de base utilisateur
    UNAUTHORIZED = "unauthorized" # Reconnu mais accès révoqué
    UNKNOWN     = "unknown"      # Visage non enregistré dans le système


# Hiérarchie des rôles pour vérifier les permissions
# Plus le niveau est élevé, plus l'accès est étendu
ROLE_HIERARCHY = {
    Role.ADMIN:        100,
    Role.ULTIMATE:     50,
    Role.PRO:          30,
    Role.USER:         10,
    Role.UNAUTHORIZED: 0,
    Role.UNKNOWN:      -1,
}

# Labels lisibles pour l'affichage dans l'interface
ROLE_LABELS = {
    Role.ADMIN:        "Administrateur",
    Role.ULTIMATE:     "Ultimate",
    Role.PRO:          "Pro",
    Role.USER:         "Utilisateur",
    Role.UNAUTHORIZED: "Non Autorisé",
    Role.UNKNOWN:      "Inconnu",
}

# Couleurs CSS associées à chaque rôle (pour les badges)
ROLE_COLORS = {
    Role.ADMIN:        "#ef4444",  # Rouge moderne — admin
    Role.ULTIMATE:     "#8b5cf6",  # Violet — ultimate
    Role.PRO:          "#f59e0b",  # Ambre — pro
    Role.USER:         "#22c55e",  # Vert — user
    Role.UNAUTHORIZED: "#ef4444",  # Rouge — bloqué
    Role.UNKNOWN:      "#94a3b8",  # Gris doux — inconnu
}


@dataclass
class User:
    """
    Représente un utilisateur du système de contrôle d'accès.
    Ce modèle sera plus tard alimenté depuis la base de données SQLite.
    """
    id: int
    name: str                          # Prénom + Nom complet
    email: str
    role: Role
    face_id: str                       # Identifiant visage (clé pour la reconnaissance faciale)
    is_active: bool = True             # Compte actif/inactif
    created_at: datetime = field(default_factory=datetime.now)
    last_access: datetime = None       # Dernier accès enregistré

    @property
    def role_label(self) -> str:
        """Retourne le label lisible du rôle."""
        return ROLE_LABELS.get(self.role, "Inconnu")

    @property
    def role_color(self) -> str:
        """Retourne la couleur CSS associée au rôle."""
        return ROLE_COLORS.get(self.role, "#95a5a6")

    def has_access(self) -> bool:
        """Vérifie si l'utilisateur a le droit d'accéder au système."""
        return self.is_active and self.role not in (Role.UNAUTHORIZED, Role.UNKNOWN)

    def has_role_at_least(self, required_role: Role) -> bool:
        """
        Vérifie si l'utilisateur a le niveau de rôle requis ou supérieur.
        Permet l'accès hiérarchique : admin voit tout, ultimate voit pro+user, etc.
        """
        user_level    = ROLE_HIERARCHY.get(self.role, -1)
        required_level = ROLE_HIERARCHY.get(required_role, -1)
        return user_level >= required_level

    def is_admin(self) -> bool:
        """Raccourci pour vérifier le rôle admin."""
        return self.role == Role.ADMIN
