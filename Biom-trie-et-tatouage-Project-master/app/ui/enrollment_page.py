# =============================================================================
# ui/enrollment_page.py
# Formulaire de demande d'inscription pour les visages inconnus
# =============================================================================

import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from app.core.router import Router
from app.services.enrollment_service import EnrollmentService
from app.resources.styles import Colors


class EnrollmentPage(QWidget):
    """
    Formulaire de demande d'inscription.
    Champs :
        - Nom complet (obligatoire)
        - Email (obligatoire, validé par regex)
        - Remarque (facultative)

    À la soumission : la demande est enregistrée dans le service
    et une confirmation visuelle est affichée (sans quitter la page).
    """

    def __init__(self, enrollment_service: EnrollmentService, parent=None):
        super().__init__(parent)
        self._service = enrollment_service
        self._setup_ui()
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

    def showEvent(self, event) -> None:
        """Réinitialise le formulaire à chaque affichage."""
        super().showEvent(event)
        self._reset_form()

    def _setup_ui(self) -> None:
        """Construit l'interface du formulaire."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # ── Carte formulaire ──────────────────────────────────────────────
        card = QFrame()
        card.setFixedWidth(500)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 14px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 36, 40, 36)
        card_layout.setSpacing(20)

        # ── En-tête ───────────────────────────────────────────────────────
        lbl_icon = QLabel("📝")
        lbl_icon.setStyleSheet("font-size: 47px; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignCenter)

        lbl_title = QLabel("Demande d'inscription")
        lbl_title.setStyleSheet(
            f"font-size: 29px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_subtitle = QLabel(
            "Remplissez ce formulaire pour soumettre une demande d'accès.\n"
            "Un administrateur examinera votre demande."
        )
        lbl_subtitle.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 19px; background: transparent; text-align: center;"
        )
        lbl_subtitle.setAlignment(Qt.AlignCenter)
        lbl_subtitle.setWordWrap(True)

        # ── Séparateur ────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; border: none; max-height: 1px;")

        # ── Champ Nom ─────────────────────────────────────────────────────
        lbl_name = QLabel("Nom complet *")
        lbl_name.setStyleSheet(
            f"font-size: 19px; font-weight: 600; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        self._input_name = QLineEdit()
        self._input_name.setPlaceholderText("ex : Alice Martin")
        self._input_name.setFixedHeight(42)

        # Label d'erreur nom
        self._err_name = QLabel("")
        self._err_name.setStyleSheet(
            f"color: {Colors.ACCENT_RED}; font-size: 18px; background: transparent;"
        )
        self._err_name.setVisible(False)

        # ── Champ Email ───────────────────────────────────────────────────
        lbl_email = QLabel("Adresse email *")
        lbl_email.setStyleSheet(
            f"font-size: 19px; font-weight: 600; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        self._input_email = QLineEdit()
        self._input_email.setPlaceholderText("ex : alice.martin@mail.com")
        self._input_email.setFixedHeight(42)

        # Label d'erreur email
        self._err_email = QLabel("")
        self._err_email.setStyleSheet(
            f"color: {Colors.ACCENT_RED}; font-size: 18px; background: transparent;"
        )
        self._err_email.setVisible(False)

        # ── Champ Remarque (facultatif) ───────────────────────────────────
        lbl_note = QLabel("Remarque (facultatif)")
        lbl_note.setStyleSheet(
            f"font-size: 19px; font-weight: 600; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        self._input_note = QTextEdit()
        self._input_note.setPlaceholderText(
            "Précisez votre service, la raison de votre demande d'accès, etc."
        )
        self._input_note.setFixedHeight(90)

        # ── Zone de confirmation (cachée initialement) ─────────────────────
        self._success_box = QFrame()
        self._success_box.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.ACCENT_GREEN}15;
                border: 1px solid {Colors.ACCENT_GREEN}55;
                border-radius: 8px;
            }}
        """)
        success_inner = QVBoxLayout(self._success_box)
        success_inner.setContentsMargins(16, 14, 16, 14)

        lbl_success = QLabel("✅  Demande envoyée avec succès !\nUn administrateur examinera votre demande.")
        lbl_success.setStyleSheet(
            f"color: {Colors.ACCENT_GREEN}; font-size: 20px; font-weight: 600; background: transparent;"
        )
        lbl_success.setwordWrap = True
        lbl_success.setAlignment(Qt.AlignCenter)
        success_inner.addWidget(lbl_success)
        self._success_box.setVisible(False)

        # ── Boutons ───────────────────────────────────────────────────────
        btn_submit = QPushButton("  ✉  Envoyer ma demande")
        btn_submit.setFixedHeight(46)
        btn_submit.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_GREEN};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 21px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #2ea043; }}
        """)
        btn_submit.clicked.connect(self._submit)

        btn_back = QPushButton("← Retour")
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

        # ── Assemblage ────────────────────────────────────────────────────
        card_layout.addWidget(lbl_icon)
        card_layout.addWidget(lbl_title)
        card_layout.addWidget(lbl_subtitle)
        card_layout.addWidget(sep)

        card_layout.addWidget(lbl_name)
        card_layout.addWidget(self._input_name)
        card_layout.addWidget(self._err_name)

        card_layout.addWidget(lbl_email)
        card_layout.addWidget(self._input_email)
        card_layout.addWidget(self._err_email)

        card_layout.addWidget(lbl_note)
        card_layout.addWidget(self._input_note)

        card_layout.addWidget(self._success_box)
        card_layout.addWidget(btn_submit)
        card_layout.addWidget(btn_back)

        main_layout.addStretch()
        main_layout.addWidget(card, alignment=Qt.AlignCenter)
        main_layout.addStretch()

    # ── Validation et soumission ──────────────────────────────────────────

    def _submit(self) -> None:
        """Valide et soumet le formulaire d'inscription."""
        # Récupérer les valeurs
        name  = self._input_name.text().strip()
        email = self._input_email.text().strip()
        note  = self._input_note.toPlainText().strip()

        # Réinitialiser les erreurs
        self._hide_errors()
        valid = True

        # Validation du nom
        if not name or len(name) < 3:
            self._err_name.setText("⚠ Veuillez saisir un nom complet (3 caractères minimum).")
            self._err_name.setVisible(True)
            self._input_name.setStyleSheet(
                f"border: 1px solid {Colors.ACCENT_RED}; border-radius: 6px; "
                f"padding: 8px 12px; background-color: {Colors.BG_TERTIARY}; color: {Colors.TEXT_PRIMARY};"
            )
            valid = False

        # Validation de l'email (regex simple)
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not email or not re.match(email_pattern, email):
            self._err_email.setText("⚠ Veuillez saisir une adresse email valide.")
            self._err_email.setVisible(True)
            self._input_email.setStyleSheet(
                f"border: 1px solid {Colors.ACCENT_RED}; border-radius: 6px; "
                f"padding: 8px 12px; background-color: {Colors.BG_TERTIARY}; color: {Colors.TEXT_PRIMARY};"
            )
            valid = False

        if not valid:
            return

        # Soumettre la demande au service
        self._service.submit_request(name=name, email=email, note=note)

        # Afficher la confirmation
        self._success_box.setVisible(True)
        self._input_name.setEnabled(False)
        self._input_email.setEnabled(False)
        self._input_note.setEnabled(False)

    def _hide_errors(self) -> None:
        """Cache les messages d'erreur et réinitialise les styles des champs."""
        for err in [self._err_name, self._err_email]:
            err.setVisible(False)

        for inp in [self._input_name, self._input_email]:
            inp.setStyleSheet("")  # Réinitialise au style global

    def _reset_form(self) -> None:
        """Vide le formulaire et réactive les champs."""
        self._input_name.clear()
        self._input_email.clear()
        self._input_note.clear()
        self._input_name.setEnabled(True)
        self._input_email.setEnabled(True)
        self._input_note.setEnabled(True)
        self._success_box.setVisible(False)
        self._hide_errors()

    def _go_back(self) -> None:
        """Retourne à la page précédente (visage inconnu)."""
        Router.get_instance().navigate("unknown_face")
