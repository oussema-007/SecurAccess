# =============================================================================
# ui/dialogs/admin_choice_dialog.py
# Dialogue de choix affiché quand un administrateur est reconnu
# =============================================================================

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from app.models.user import User
from app.resources.styles import Colors


class AdminChoiceDialog(QDialog):
    """
    Dialogue modal affiché lorsqu'un administrateur est reconnu.
    Propose trois choix :
      1. Accéder au dashboard admin
      2. Continuer comme utilisateur normal
      3. Annuler (retour à la page de login)

    Usage :
        dialog = AdminChoiceDialog(user=admin_user, parent=self)
        choice = dialog.exec_()
        if choice == AdminChoiceDialog.CHOICE_DASHBOARD: ...
    """

    # Codes de retour personnalisés
    CHOICE_DASHBOARD = 2   # Accéder au dashboard admin
    CHOICE_USER      = 1   # Continuer comme utilisateur normal
    CHOICE_CANCEL    = 0   # Annuler

    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self._user = user
        self.setWindowTitle("Administrateur reconnu")
        self.setModal(True)
        self.setFixedWidth(420)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Construit l'interface du dialogue."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(20)

        # ── En-tête ───────────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        icon_label = QLabel("🔐")
        icon_label.setStyleSheet("font-size: 43px; background: transparent;")
        icon_label.setFixedWidth(48)

        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        lbl_title = QLabel("Administrateur reconnu")
        lbl_title.setStyleSheet(
            f"font-size: 23px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )

        lbl_name = QLabel(f"Bienvenue, {self._user.name}")
        lbl_name.setStyleSheet(
            f"font-size: 20px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        header_text.addWidget(lbl_title)
        header_text.addWidget(lbl_name)
        header_layout.addWidget(icon_label)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # ── Séparateur ────────────────────────────────────────────────────
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Colors.BORDER}; border: none; max-height: 1px;")

        # ── Message ───────────────────────────────────────────────────────
        lbl_msg = QLabel("Votre compte dispose des droits administrateurs.\nComment souhaitez-vous vous connecter ?")
        lbl_msg.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 20px; line-height: 1.6; background: transparent;"
        )
        lbl_msg.setWordWrap(True)

        # ── Bouton Dashboard Admin ────────────────────────────────────────
        btn_dashboard = QPushButton("  🖥  Accéder au Dashboard Admin")
        btn_dashboard.setFixedHeight(46)
        btn_dashboard.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_RED};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 21px;
                font-weight: 600;
                text-align: left;
                padding-left: 16px;
            }}
            QPushButton:hover {{ background-color: #f85149; }}
        """)
        btn_dashboard.clicked.connect(self._choose_dashboard)

        # ── Bouton Utilisateur normal ─────────────────────────────────────
        btn_user = QPushButton("  👤  Continuer comme Utilisateur")
        btn_user.setFixedHeight(46)
        btn_user.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 21px;
                font-weight: 600;
                text-align: left;
                padding-left: 16px;
            }}
            QPushButton:hover {{ background-color: #388bfd; }}
        """)
        btn_user.clicked.connect(self._choose_user)

        # ── Bouton Annuler ────────────────────────────────────────────────
        btn_cancel = QPushButton("Annuler")
        btn_cancel.setFixedHeight(38)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 20px;
            }}
            QPushButton:hover {{ border-color: {Colors.TEXT_PRIMARY}; color: {Colors.TEXT_PRIMARY}; }}
        """)
        btn_cancel.clicked.connect(self._choose_cancel)

        # ── Assemblage ────────────────────────────────────────────────────
        layout.addLayout(header_layout)
        layout.addWidget(separator)
        layout.addWidget(lbl_msg)
        layout.addWidget(btn_dashboard)
        layout.addWidget(btn_user)
        layout.addWidget(btn_cancel)

    def _choose_dashboard(self) -> None:
        """L'admin choisit d'aller au dashboard."""
        self.done(self.CHOICE_DASHBOARD)

    def _choose_user(self) -> None:
        """L'admin choisit de continuer comme utilisateur."""
        self.done(self.CHOICE_USER)

    def _choose_cancel(self) -> None:
        """L'admin annule et retourne à la page de login."""
        self.done(self.CHOICE_CANCEL)
