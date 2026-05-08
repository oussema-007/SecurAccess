# =============================================================================
# ui/components/role_badge.py
# Badge de rôle coloré réutilisable
# =============================================================================

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
from app.models.user import Role, ROLE_LABELS, ROLE_COLORS


class RoleBadge(QLabel):
    """
    Petit badge coloré indiquant le rôle d'un utilisateur.
    Réutilisé dans le tableau des utilisateurs, les logs, la welcome page, etc.

    Usage :
        badge = RoleBadge(role=Role.ADMIN)
        badge = RoleBadge(role=Role.PRO)
    """

    def __init__(self, role: Role, parent=None):
        super().__init__(parent)
        self.set_role(role)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(24)

    def set_role(self, role: Role) -> None:
        """Applique le style et le texte correspondant au rôle donné."""
        label = ROLE_LABELS.get(role, "Inconnu")
        color = ROLE_COLORS.get(role, "#95a5a6")

        self.setText(label.upper())
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: 600;
                font-size: 11px;
                padding: 3px 10px;
                border-radius: 12px;
                background-color: {color}18;
                border: 1px solid {color}40;
                letter-spacing: 0.5px;
            }}
        """)


class StatusBadge(QLabel):
    """
    Badge de statut (Autorisé / Refusé / Inconnu) pour les logs.
    """

    STATUS_STYLES = {
        "Autorisé":  ("✓ AUTORISÉ",  "#22c55e"),
        "Admin":     ("⭐ ADMIN",     "#3b82f6"),
        "Refusé":    ("✗ REFUSÉ",    "#ef4444"),
        "Inconnu":   ("? INCONNU",   "#f59e0b"),
        "En attente": ("⏳ EN ATTENTE", "#f59e0b"),
        "Approuvée": ("✓ APPROUVÉE", "#22c55e"),
        "Rejetée":   ("✗ REJETÉE",   "#ef4444"),
    }

    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)
        self.setAlignment(Qt.AlignCenter)

    def set_status(self, status: str) -> None:
        """Applique le style selon le statut."""
        text, color = self.STATUS_STYLES.get(status, (status.upper(), "#94a3b8"))
        self.setText(text)
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: 600;
                font-size: 11px;
                padding: 3px 10px;
                border-radius: 12px;
                background-color: {color}12;
                border: 1px solid {color}30;
            }}
        """)


class IntegrityBadge(QLabel):
    """Badge d'intégrité du watermark (OK / CORROMPU)."""

    def __init__(self, is_ok: bool, parent=None):
        super().__init__(parent)
        self.set_integrity(is_ok)
        self.setAlignment(Qt.AlignCenter)

    def set_integrity(self, is_ok: bool) -> None:
        if is_ok:
            self.setText("✓ INTACT")
            self.setStyleSheet("""
                QLabel {
                    color: #22c55e;
                    font-weight: 600;
                    font-size: 11px;
                    padding: 3px 10px;
                    border-radius: 12px;
                    background-color: #22c55e12;
                    border: 1px solid #22c55e30;
                }
            """)
        else:
            self.setText("⚠ CORROMPU")
            self.setStyleSheet("""
                QLabel {
                    color: #ef4444;
                    font-weight: 600;
                    font-size: 11px;
                    padding: 3px 10px;
                    border-radius: 12px;
                    background-color: #ef444412;
                    border: 1px solid #ef444430;
                }
            """)
