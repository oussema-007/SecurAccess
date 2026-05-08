# =============================================================================
# ui/unknown_face_page.py
# Page affichée quand le visage n'est pas reconnu dans le système
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from app.core.router import Router
from app.core.session import Session
from app.resources.styles import Colors


class UnknownFacePage(QWidget):
    """
    Page affichée quand le visage n'est pas reconnu du tout.
    Propose à l'utilisateur de soumettre une demande d'inscription.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._custom_message = ""
        self._setup_ui()
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(40, 40, 40, 40)

        # ── Carte centrale ────────────────────────────────────────────────
        card = QFrame()
        card.setFixedWidth(480)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-top: 4px solid {Colors.ACCENT_ORANGE};
                border-radius: 14px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 36)
        card_layout.setSpacing(18)
        card_layout.setAlignment(Qt.AlignTop)

        # Icône
        lbl_icon = QLabel("❓")
        lbl_icon.setStyleSheet("font-size: 63px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        # Titre
        lbl_title = QLabel("Visage Inconnu")
        lbl_title.setStyleSheet(
            f"font-size: 31px; font-weight: 700; color: {Colors.ACCENT_ORANGE}; background: transparent;"
        )
        lbl_title.setAlignment(Qt.AlignCenter)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; border: none; max-height: 1px;")

        # Explication
        self._lbl_desc = QLabel(
            "Votre visage n'a pas été reconnu dans notre système.\n\n"
            "Si vous êtes un nouvel utilisateur ou si vous n'avez pas encore été "
            "enregistré, vous pouvez soumettre une demande d'accès. "
            "Elle sera examinée par un administrateur."
        )
        self._lbl_desc.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 20px; background: transparent; line-height: 1.6;"
        )
        self._lbl_desc.setAlignment(Qt.AlignCenter)
        self._lbl_desc.setWordWrap(True)

        # Encart information
        info_box = QFrame()
        info_box.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.ACCENT_ORANGE}15;
                border: 1px solid {Colors.ACCENT_ORANGE}44;
                border-radius: 8px;
            }}
        """)
        info_inner = QVBoxLayout(info_box)
        info_inner.setContentsMargins(14, 12, 14, 12)
        lbl_info = QLabel(
            "⚠️  Aucun compte ne correspond à vos données biométriques. "
            "La demande d'inscription ne crée pas de compte immédiatement — "
            "elle sera validée par un administrateur."
        )
        lbl_info.setStyleSheet(
            f"color: {Colors.ACCENT_ORANGE}; font-size: 19px; background: transparent;"
        )
        lbl_info.setWordWrap(True)
        info_inner.addWidget(lbl_info)

        # Bouton : soumettre une demande
        btn_enroll = QPushButton("  📝  Demander une inscription")
        btn_enroll.setFixedHeight(46)
        btn_enroll.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_ORANGE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 21px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #f0a500; }}
        """)
        btn_enroll.clicked.connect(self._go_to_enrollment)

        # Bouton : retour
        btn_back = QPushButton("← Retour à la connexion")
        btn_back.setFixedHeight(38)
        btn_back.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 20px;
            }}
            QPushButton:hover {{ border-color: {Colors.TEXT_PRIMARY}; color: {Colors.TEXT_PRIMARY}; }}
        """)
        btn_back.clicked.connect(self._go_back)

        # Assemblage
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(sep)
        card_layout.addWidget(self._lbl_desc)
        card_layout.addWidget(info_box)
        card_layout.addSpacing(4)
        card_layout.addWidget(btn_enroll)
        card_layout.addWidget(btn_back)

        layout.addStretch()
        layout.addWidget(card, alignment=Qt.AlignCenter)
        layout.addStretch()

    def _go_to_enrollment(self) -> None:
        """Navigue vers le formulaire de demande d'inscription."""
        Router.get_instance().navigate("enrollment")

    def _go_back(self) -> None:
        """Retourne à la page de login."""
        Router.get_instance().navigate("login")

    def set_message(self, message: str) -> None:
        """Permet au controleur de personnaliser le message d'inconnu."""
        if message:
            self._custom_message = message
            self._lbl_desc.setText(
                f"{message}\n\n"
                "Si vous etes un nouvel utilisateur, vous pouvez soumettre "
                "une demande d'inscription."
            )
