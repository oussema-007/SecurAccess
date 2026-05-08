# =============================================================================
# ui/access_denied_page.py
# Page affichée quand un utilisateur est reconnu mais non autorisé
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from app.core.router import Router
from app.core.session import Session
from app.resources.styles import Colors


class AccessDeniedPage(QWidget):
    """
    Page d'accès refusé.
    S'affiche quand le visage est reconnu mais le compte n'est pas autorisé.
    Affiche le nom de l'utilisateur, la raison du refus, et un retour au login.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._custom_reason = ""
        self._setup_ui()

    def showEvent(self, event) -> None:
        """Actualise les informations de l'utilisateur refusé à chaque affichage."""
        super().showEvent(event)
        self._refresh_user_info()

    def _setup_ui(self) -> None:
        """Construit l'interface de la page de refus."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)

        # ── Carte centrale ────────────────────────────────────────────────
        card = QFrame()
        card.setFixedWidth(480)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-top: 4px solid {Colors.ACCENT_RED};
                border-radius: 14px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 36)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignTop)

        # ── Icône ─────────────────────────────────────────────────────────
        lbl_icon = QLabel("🚫")
        lbl_icon.setStyleSheet("font-size: 63px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        # ── Titre ─────────────────────────────────────────────────────────
        lbl_title = QLabel("Accès Refusé")
        lbl_title.setStyleSheet(
            f"font-size: 33px; font-weight: 700; color: {Colors.ACCENT_RED}; background: transparent;"
        )
        lbl_title.setAlignment(Qt.AlignCenter)

        # ── Nom utilisateur (mis à jour dynamiquement) ─────────────────────
        self._lbl_user = QLabel("")
        self._lbl_user.setStyleSheet(
            f"font-size: 22px; color: {Colors.TEXT_PRIMARY}; font-weight: 600; background: transparent;"
        )
        self._lbl_user.setAlignment(Qt.AlignCenter)

        # ── Séparateur ─────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; border: none; max-height: 1px;")

        # ── Explication ────────────────────────────────────────────────────
        self._lbl_reason = QLabel("")
        self._lbl_reason.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 20px; line-height: 1.6; background: transparent;"
        )
        self._lbl_reason.setAlignment(Qt.AlignCenter)
        self._lbl_reason.setWordWrap(True)

        # ── Encart d'information ───────────────────────────────────────────
        info_box = QFrame()
        info_box.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.ACCENT_RED}15;
                border: 1px solid {Colors.ACCENT_RED}44;
                border-radius: 8px;
            }}
        """)
        info_layout = QVBoxLayout(info_box)
        info_layout.setContentsMargins(16, 14, 16, 14)

        lbl_info = QLabel(
            "ℹ️  Si vous pensez qu'il s'agit d'une erreur, veuillez "
            "contacter votre administrateur système."
        )
        lbl_info.setStyleSheet(
            f"color: {Colors.ACCENT_RED}; font-size: 19px; background: transparent;"
        )
        lbl_info.setWordWrap(True)
        info_layout.addWidget(lbl_info)

        # ── Bouton retour ──────────────────────────────────────────────────
        btn_back = QPushButton("← Retour à la page de connexion")
        btn_back.setFixedHeight(44)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_TERTIARY};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 21px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border-color: {Colors.TEXT_SECONDARY};
            }}
        """)
        btn_back.clicked.connect(self._go_back)

        # ── Assemblage ─────────────────────────────────────────────────────
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(self._lbl_user)
        card_layout.addWidget(sep)
        card_layout.addWidget(self._lbl_reason)
        card_layout.addWidget(info_box)
        card_layout.addSpacing(8)
        card_layout.addWidget(btn_back)

        layout.addStretch()
        layout.addWidget(card, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

    def _refresh_user_info(self) -> None:
        """Met à jour le nom et la raison du refus selon la session courante."""
        user = Session.get_instance().current_user
        base_reason = self._custom_reason
        if user:
            self._lbl_user.setText(f"Identité : {user.name}")
            self._lbl_reason.setText(base_reason or (
                f"Votre compte ({user.email}) a été reconnu dans le système "
                f"mais votre accès a été révoqué ou désactivé par un administrateur.\n\n"
                f"Statut du compte : {user.role_label}"
            ))
        else:
            self._lbl_user.setText("Identité : Non disponible")
            self._lbl_reason.setText(base_reason or "L'accès à ce système vous a été refusé.")

    def set_reason(self, reason: str) -> None:
        """Permet au contrôleur de fournir une raison explicite."""
        self._custom_reason = reason or ""

    def _go_back(self) -> None:
        """Retourne à la page de login et nettoie la session."""
        Session.get_instance().logout()
        Router.get_instance().navigate("login")
