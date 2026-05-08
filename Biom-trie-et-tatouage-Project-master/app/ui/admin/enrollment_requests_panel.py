# =============================================================================
# ui/admin/enrollment_requests_panel.py
# Panneau de gestion des demandes d'inscription
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from app.ui.components.role_badge import StatusBadge
from app.services.enrollment_service import EnrollmentService
from app.models.enrollment_request import RequestStatus
from app.core.session import Session
from app.resources.styles import Colors


class EnrollmentRequestsPanel(QWidget):
    """
    Panneau de traitement des demandes d'inscription.
    L'admin peut approuver ou rejeter chaque demande depuis ce panneau.
    """

    def __init__(self, enrollment_service: EnrollmentService, parent=None):
        super().__init__(parent)
        self._service = enrollment_service
        self._setup_ui()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._load_requests()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

        # ── En-tête ────────────────────────────────────────────────────────
        lbl_title = QLabel("Demandes d'Inscription")
        lbl_title.setStyleSheet(
            f"font-size: 27px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_sub = QLabel("Validez ou rejetez les demandes d'accès soumises par les visiteurs.")
        lbl_sub.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        # Compteur
        self._lbl_count = QLabel()
        self._lbl_count.setStyleSheet(
            f"font-size: 19px; color: {Colors.ACCENT_ORANGE}; font-weight: 600; background: transparent;"
        )

        # ── Tableau ────────────────────────────────────────────────────────
        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels([
            "ID", "Nom", "Email", "Remarque", "Soumis le", "Statut", "Actions"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self._table.setColumnWidth(6, 190)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                alternate-background-color: {Colors.BG_TERTIARY};
            }}
        """)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        layout.addWidget(self._lbl_count)
        layout.addWidget(self._table)

    def _load_requests(self) -> None:
        """Charge toutes les demandes depuis le service."""
        requests = self._service.get_all_requests()
        pending  = self._service.get_pending_requests()

        self._lbl_count.setText(
            f"⏳  {len(pending)} demande(s) en attente sur {len(requests)} total"
        )

        self._table.setRowCount(len(requests))

        for row, req in enumerate(requests):
            self._table.setRowHeight(row, 54)

            # ID
            id_item = QTableWidgetItem(str(req.id))
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 0, id_item)

            # Nom
            name_item = QTableWidgetItem(req.name)
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            self._table.setItem(row, 1, name_item)

            # Email
            email_item = QTableWidgetItem(req.email)
            email_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self._table.setItem(row, 2, email_item)

            # Remarque
            note_item = QTableWidgetItem(req.note if req.note else "—")
            note_item.setForeground(QColor(Colors.TEXT_MUTED))
            self._table.setItem(row, 3, note_item)

            # Date soumission
            date_item = QTableWidgetItem(req.submitted_at.strftime("%d/%m/%Y %H:%M"))
            date_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self._table.setItem(row, 4, date_item)

            # Statut (badge)
            status_w = QWidget()
            sl = QHBoxLayout(status_w)
            sl.setContentsMargins(6, 2, 6, 2)
            sl.addStretch()
            sl.addWidget(StatusBadge(req.status_label))
            sl.addStretch()
            self._table.setCellWidget(row, 5, status_w)

            # Boutons d'action (seulement pour les demandes en attente)
            if req.status == RequestStatus.PENDING:
                actions_w = self._build_action_buttons(req.id)
                self._table.setCellWidget(row, 6, actions_w)
            else:
                # Afficher qui a traité la demande
                processed_item = QTableWidgetItem(
                    f"Traité par {req.processed_by}" if req.processed_by else "—"
                )
                processed_item.setForeground(QColor(Colors.TEXT_MUTED))
                self._table.setItem(row, 6, processed_item)

    def _build_action_buttons(self, request_id: int) -> QWidget:
        """Construit les boutons Approuver / Rejeter pour une demande."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        btn_approve = QPushButton("✓ Approuver")
        btn_approve.setFixedHeight(30)
        btn_approve.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_GREEN};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{ background-color: #2ea043; }}
        """)
        btn_approve.clicked.connect(lambda checked, rid=request_id: self._approve(rid))

        btn_reject = QPushButton("✗ Rejeter")
        btn_reject.setFixedHeight(30)
        btn_reject.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_RED};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 18px;
                font-weight: 600;
                padding: 0 10px;
            }}
            QPushButton:hover {{ background-color: #f85149; }}
        """)
        btn_reject.clicked.connect(lambda checked, rid=request_id: self._reject(rid))

        layout.addWidget(btn_approve)
        layout.addWidget(btn_reject)
        layout.addStretch()

        return widget

    def _approve(self, request_id: int) -> None:
        """Approuve la demande et recharge la liste."""
        admin = Session.get_instance().current_user
        admin_name = admin.name if admin else "Administrateur"
        self._service.approve_request(request_id, admin_name)
        self._load_requests()

    def _reject(self, request_id: int) -> None:
        """Rejette la demande et recharge la liste."""
        admin = Session.get_instance().current_user
        admin_name = admin.name if admin else "Administrateur"
        self._service.reject_request(request_id, admin_name)
        self._load_requests()
