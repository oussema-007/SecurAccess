# =============================================================================
# ui/admin/settings_panel.py
# Panneau des paramètres du système
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QCheckBox, QComboBox, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt
from app.resources.styles import Colors


class SettingsPanel(QWidget):
    """
    Panneau des paramètres de configuration du système.
    [Futur] Ces paramètres seront persistés dans SQLite ou un fichier .ini.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(24)

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # ── Titre ──────────────────────────────────────────────────────────
        lbl_title = QLabel("Paramètres du système")
        lbl_title.setStyleSheet(
            f"font-size: 27px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_sub = QLabel("Configuration générale du système de contrôle d'accès.")
        lbl_sub.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)

        # ── Section Reconnaissance Faciale ─────────────────────────────────
        layout.addWidget(self._build_group(
            "🎯  Reconnaissance Faciale",
            [
                self._build_setting_row(
                    "Seuil de confiance minimal",
                    "Score minimum pour accepter une reconnaissance (0.0 – 1.0)",
                    QLineEdit("0.80"),
                ),
                self._build_setting_row(
                    "Nombre d'essais autorisés",
                    "Nombre maximum de tentatives avant alerte",
                    QLineEdit("3"),
                ),
                self._build_setting_row(
                    "Algorithme de classification",
                    "Modèle scikit-learn utilisé pour la reconnaissance",
                    self._make_combo(["SVM (recommandé)", "KNN", "Random Forest"]),
                ),
                self._build_checkbox_row(
                    "Activer le mode débogage caméra",
                    "Affiche les bounding boxes et scores sur le flux vidéo",
                    False,
                ),
            ]
        ))

        # ── Section Notifications email ────────────────────────────────────
        layout.addWidget(self._build_group(
            "📧  Notifications Email (SMTP)",
            [
                self._build_setting_row(
                    "Serveur SMTP",
                    "Adresse du serveur d'envoi",
                    QLineEdit("smtp.gmail.com"),
                ),
                self._build_setting_row(
                    "Port SMTP",
                    "Port de connexion (587 = TLS)",
                    QLineEdit("587"),
                ),
                self._build_setting_row(
                    "Email expéditeur",
                    "Compte email utilisé pour l'envoi des alertes",
                    QLineEdit("securaccess.alerts@gmail.com"),
                ),
                self._build_setting_row(
                    "Email destinataire",
                    "Email de l'administrateur qui reçoit les alertes",
                    QLineEdit("admin@votre-organisation.fr"),
                ),
                self._build_checkbox_row(
                    "Envoyer une alerte sur accès refusé",
                    "Notifie l'admin à chaque accès refusé",
                    True,
                ),
                self._build_checkbox_row(
                    "Envoyer une alerte sur visage inconnu",
                    "Notifie l'admin à chaque visage non reconnu",
                    True,
                ),
            ]
        ))

        # ── Section Sécurité & Logs ────────────────────────────────────────
        layout.addWidget(self._build_group(
            "🔐  Sécurité & Intégrité des Logs",
            [
                self._build_setting_row(
                    "Clé secrète HMAC",
                    "Clé utilisée pour le tatouage numérique des logs [masquée]",
                    self._make_password_field("••••••••••••••••••••••••"),
                ),
                self._build_setting_row(
                    "Durée de conservation des logs (jours)",
                    "Supprime automatiquement les logs plus anciens",
                    QLineEdit("90"),
                ),
                self._build_checkbox_row(
                    "Vérification automatique d'intégrité au démarrage",
                    "Lance une vérification HMAC à chaque démarrage de l'application",
                    True,
                ),
            ]
        ))

        # ── Bouton sauvegarde ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_save = QPushButton("  💾  Sauvegarder les paramètres")
        btn_save.setFixedHeight(44)
        btn_save.setFixedWidth(260)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #388bfd; }}
        """)
        btn_save.clicked.connect(self._save_settings)

        btn_reset = QPushButton("Réinitialiser")
        btn_reset.setFixedHeight(44)
        btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 20px;
                padding: 0 18px;
            }}
            QPushButton:hover {{ border-color: {Colors.TEXT_PRIMARY}; color: {Colors.TEXT_PRIMARY}; }}
        """)

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_reset)
        btn_row.addStretch()

        layout.addLayout(btn_row)
        layout.addStretch()

        # Label confirmation sauvegarde
        self._lbl_saved = QLabel("")
        self._lbl_saved.setStyleSheet(
            f"color: {Colors.ACCENT_GREEN}; font-size: 19px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(self._lbl_saved)

    # ── Constructeurs de widgets de paramètres ────────────────────────────

    def _build_group(self, title: str, rows: list) -> QGroupBox:
        """Construit un groupe de paramètres avec un titre de section."""
        group = QGroupBox(title)
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                margin-top: 14px;
                padding-top: 14px;
                font-weight: 700;
                font-size: 20px;
                background-color: {Colors.BG_SECONDARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                background-color: {Colors.BG_SECONDARY};
            }}
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        for row in rows:
            layout.addWidget(row)
        return group

    def _build_setting_row(self, label: str, hint: str, widget: QWidget) -> QFrame:
        """Construit une ligne de paramètre avec label, description et widget de saisie."""
        frame = QFrame()
        frame.setStyleSheet("QFrame { background: transparent; }")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        text_block = QVBoxLayout()
        text_block.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size: 20px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_hint = QLabel(hint)
        lbl_hint.setStyleSheet(
            f"font-size: 18px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        text_block.addWidget(lbl)
        text_block.addWidget(lbl_hint)

        widget.setFixedWidth(220)
        widget.setFixedHeight(36)

        layout.addLayout(text_block, stretch=1)
        layout.addWidget(widget)

        return frame

    def _build_checkbox_row(self, label: str, hint: str, checked: bool) -> QFrame:
        """Construit une ligne de paramètre booléen avec checkbox."""
        frame = QFrame()
        frame.setStyleSheet("QFrame { background: transparent; }")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        text_block = QVBoxLayout()
        text_block.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size: 20px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_hint = QLabel(hint)
        lbl_hint.setStyleSheet(
            f"font-size: 18px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        text_block.addWidget(lbl)
        text_block.addWidget(lbl_hint)

        cb = QCheckBox()
        cb.setChecked(checked)
        cb.setFixedSize(22, 22)

        layout.addLayout(text_block, stretch=1)
        layout.addWidget(cb)

        return frame

    def _make_combo(self, options: list) -> QComboBox:
        """Crée une combobox avec les options données."""
        cb = QComboBox()
        for opt in options:
            cb.addItem(opt)
        return cb

    def _make_password_field(self, value: str) -> QLineEdit:
        """Crée un champ mot de passe masqué."""
        field = QLineEdit(value)
        field.setEchoMode(QLineEdit.Password)
        return field

    def _save_settings(self) -> None:
        """
        [Futur] Sauvegarde les paramètres en base SQLite ou config file.
        Pour l'instant : affiche une confirmation visuelle.
        """
        self._lbl_saved.setText("✅  Paramètres sauvegardés avec succès!")
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self._lbl_saved.setText(""))
