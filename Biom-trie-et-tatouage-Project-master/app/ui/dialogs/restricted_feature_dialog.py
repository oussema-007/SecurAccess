# =============================================================================
# ui/dialogs/restricted_feature_dialog.py
# Dialogue affiché lors du clic sur une fonctionnalité restreinte
# =============================================================================

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from app.models.user import Role, ROLE_LABELS
from app.resources.styles import Colors


class RestrictedFeatureDialog(QDialog):
    """
    Dialogue modal informant l'utilisateur qu'il tente d'accéder à 
    une fonctionnalité nécessitant un rôle supérieur, et lui 
    proposant de faire une demande d'évolution.
    """

    # Codes de retour
    CHOICE_UPGRADE_REQUEST = 1
    CHOICE_CANCEL          = 0

    def __init__(self, feature_name: str, required_role: Role, current_role: Role, parent=None):
        super().__init__(parent)
        self._feature_name  = feature_name
        self._required_role = required_role
        self._current_role  = current_role
        
        self.setWindowTitle("Fonctionnalité Restreinte")
        self.setModal(True)
        self.setFixedWidth(460)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-top: 4px solid {Colors.ACCENT_PURPLE};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(20)

        # ── En-tête ───────────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        icon_label = QLabel("⭐")
        icon_label.setStyleSheet("font-size: 45px; background: transparent;")
        icon_label.setFixedWidth(48)

        header_text = QVBoxLayout()
        header_text.setSpacing(4)

        lbl_title = QLabel("Fonctionnalité Premium")
        lbl_title.setStyleSheet(
            f"font-size: 23px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )

        lbl_feat = QLabel(f"Section : {self._feature_name}")
        lbl_feat.setStyleSheet(
            f"font-size: 20px; color: {Colors.ACCENT_PURPLE}; font-weight: 600; background: transparent;"
        )

        header_text.addWidget(lbl_title)
        header_text.addWidget(lbl_feat)
        header_layout.addWidget(icon_label)
        header_layout.addLayout(header_text)
        header_layout.addStretch()

        # ── Séparateur ────────────────────────────────────────────────────
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Colors.BORDER}; border: none; max-height: 1px;")

        # ── Messages ──────────────────────────────────────────────────────
        req_name = ROLE_LABELS.get(self._required_role, "Supérieur")
        
        lbl_msg = QLabel(
            f"Cette fonctionnalité exclusive est réservée aux comptes disposant "
            f"du niveau <b>{req_name}</b> ou supérieur."
        )
        lbl_msg.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 20px; line-height: 1.6; background: transparent;"
        )
        lbl_msg.setWordWrap(True)
        lbl_msg.setTextFormat(Qt.RichText)

        info_box = QFrame()
        info_box.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.ACCENT_PURPLE}15;
                border: 1px solid {Colors.ACCENT_PURPLE}44;
                border-radius: 8px;
            }}
        """)
        info_l = QVBoxLayout(info_box)
        info_l.setContentsMargins(14, 12, 14, 12)
        
        lbl_benefit = QLabel(
            "🚀 <b>Passez au niveau supérieur !</b><br>"
            "Demandez une évolution de votre compte pour débloquer de nouveaux outils, "
            "des rapports avancés, et bien plus encore."
        )
        lbl_benefit.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 19px; background: transparent;")
        lbl_benefit.setWordWrap(True)
        lbl_benefit.setTextFormat(Qt.RichText)
        info_l.addWidget(lbl_benefit)

        # ── Boutons d'action ──────────────────────────────────────────────
        btn_upgrade = QPushButton("  ⭐  Faire une demande d'évolution")
        btn_upgrade.setFixedHeight(46)
        btn_upgrade.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PURPLE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 21px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #a371f7; }}
        """)
        btn_upgrade.clicked.connect(self._choose_upgrade)

        btn_cancel = QPushButton("Plus tard")
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

        # Assemblage
        layout.addLayout(header_layout)
        layout.addWidget(separator)
        layout.addWidget(lbl_msg)
        layout.addWidget(info_box)
        layout.addSpacing(6)
        layout.addWidget(btn_upgrade)
        layout.addWidget(btn_cancel)

    def _choose_upgrade(self) -> None:
        self.done(self.CHOICE_UPGRADE_REQUEST)

    def _choose_cancel(self) -> None:
        self.done(self.CHOICE_CANCEL)
