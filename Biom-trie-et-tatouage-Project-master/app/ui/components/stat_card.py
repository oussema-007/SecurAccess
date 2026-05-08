# =============================================================================
# ui/components/stat_card.py
# Carte statistique réutilisable pour le dashboard admin
# =============================================================================

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from app.resources.styles import Colors


class StatCard(QFrame):
    """
    Widget carte statistique affichant :
    - Une icône (emoji ou caractère Unicode)
    - Un titre descriptif
    - Une valeur numérique en grand
    - Une couleur d'accentuation

    Usage :
        card = StatCard(
            title="Accès autorisés",
            value="124",
            icon="✅",
            accent_color=Colors.ACCENT_GREEN
        )
    """

    def __init__(self, title: str, value: str, icon: str = "📊",
                 accent_color: str = Colors.ACCENT_BLUE, parent=None):
        super().__init__(parent)

        self.setObjectName("stat_card")
        self.setFixedHeight(120)
        self.setCursor(Qt.PointingHandCursor)

        # Modern white card with soft shadow and top accent
        self.setStyleSheet(f"""
            QFrame#stat_card {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-top: 3px solid {accent_color};
                border-radius: 16px;
            }}
            QFrame#stat_card:hover {{
                border-color: {accent_color}88;
                border-top: 3px solid {accent_color};
            }}
        """)

        # Subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 12))
        self.setGraphicsEffect(shadow)

        # ── Layout principal ──────────────────────────────────────────────
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # ── Colonne gauche : texte ────────────────────────────────────────
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)

        # Titre de la carte
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: 500;")

        # Valeur principale (grande et visible)
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 32px; font-weight: 700; letter-spacing: -1px;")
        lbl_value.setObjectName("card_value")  # Pour mise à jour dynamique

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        text_layout.addStretch()

        # ── Colonne droite : icône ────────────────────────────────────────
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet(f"font-size: 32px; color: {accent_color};")
        lbl_icon.setAlignment(Qt.AlignCenter)

        # Assemblage
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(lbl_icon)

        # Références pour mise à jour dynamique
        self._lbl_value = lbl_value
        self._lbl_title = lbl_title

    def update_value(self, new_value: str) -> None:
        """Met à jour la valeur affichée (pour rafraîchissement des stats)."""
        self._lbl_value.setText(new_value)

    def update_title(self, new_title: str) -> None:
        """Met à jour le titre de la carte."""
        self._lbl_title.setText(new_title)
