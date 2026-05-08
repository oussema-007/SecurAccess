# =============================================================================
# ui/admin/overview_panel.py
# Panneau "Vue d'ensemble" du dashboard admin
# =============================================================================

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from app.ui.components.stat_card import StatCard
from app.ui.components.role_badge import StatusBadge
from app.services.log_service import LogService
from app.services.enrollment_service import EnrollmentService
from app.resources.styles import Colors


class OverviewPanel(QWidget):
    """
    Panneau principal du dashboard admin.
    Affiche :
    - 6 cartes de statistiques clés
    - Tableau des 5 derniers événements
    - Liste des demandes en attente
    """

    def __init__(self, log_service: LogService,
                 enrollment_service: EnrollmentService, parent=None):
        super().__init__(parent)
        self._log_service    = log_service
        self._enroll_service = enrollment_service
        self._setup_ui()

    def showEvent(self, event) -> None:
        """Rafraîchit les données à chaque affichage du panneau."""
        super().showEvent(event)
        self._refresh_data()

    def _setup_ui(self) -> None:
        """Construit l'interface du panneau."""
        # Zone scrollable pour tout le contenu
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._container.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(28, 24, 28, 28)
        self._layout.setSpacing(24)

        scroll.setWidget(self._container)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # ── Titre ──────────────────────────────────────────────────────────
        header = QVBoxLayout()
        lbl_title = QLabel("Vue d'ensemble")
        lbl_title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; letter-spacing: -0.5px;"
        )
        lbl_date = QLabel(datetime.now().strftime("Aujourd'hui — %A %d %B %Y"))
        lbl_date.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        header.addWidget(lbl_title)
        header.addWidget(lbl_date)
        self._layout.addLayout(header)

        # ── Grille de stats ────────────────────────────────────────────────
        self._stats_grid = QGridLayout()
        self._stats_grid.setSpacing(16)

        # Les cartes seront créées dans _refresh_data()
        self._layout.addLayout(self._stats_grid)

        # ── Séparateur ─────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background: {Colors.BORDER}; border: none; max-height: 1px;")
        self._layout.addWidget(sep)

        # ── Ligne : logs + demandes ────────────────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(20)

        self._recent_logs_frame   = self._build_recent_logs_frame()
        self._pending_enroll_frame = self._build_pending_enrollments_frame()

        bottom_row.addWidget(self._recent_logs_frame, stretch=3)
        bottom_row.addWidget(self._pending_enroll_frame, stretch=2)
        self._layout.addLayout(bottom_row)
        self._layout.addStretch()

    def _refresh_data(self) -> None:
        """Recharge toutes les statistiques depuis les services."""
        log_stats    = self._log_service.get_stats()
        enroll_stats = self._enroll_service.get_stats()

        # Vider l'ancienne grille de stats
        while self._stats_grid.count():
            item = self._stats_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Définition des cartes
        cards_data = [
            ("Utilisateurs totaux",  "8",                          "👥", Colors.ACCENT_BLUE),
            ("Accès autorisés",       str(log_stats["allowed"]),    "✅", Colors.ACCENT_GREEN),
            ("Accès refusés",         str(log_stats["denied"]),     "🚫", Colors.ACCENT_RED),
            ("Visages inconnus",      str(log_stats["unknown"]),    "❓", Colors.ACCENT_ORANGE),
            ("Demandes en attente",   str(enroll_stats["pending"]), "📝", Colors.ACCENT_PURPLE),
            ("Total logs",            str(log_stats["total"]),      "📋", Colors.ACCENT_TEAL),
        ]

        for i, (title, value, icon, color) in enumerate(cards_data):
            card = StatCard(title=title, value=value, icon=icon, accent_color=color)
            self._stats_grid.addWidget(card, i // 3, i % 3)

        # Rafraîchir les tableaux
        self._refresh_logs_table()
        self._refresh_pending_table()

    def _build_recent_logs_frame(self) -> QFrame:
        """Construit l'encadré des logs récents."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl = QLabel("Événements récents")
        lbl.setStyleSheet(
            f"font-weight: 600; font-size: 15px; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )

        self._logs_table = QTableWidget(0, 4)
        self._logs_table.setHorizontalHeaderLabels(["Utilisateur", "Rôle", "Statut", "Heure"])
        self._logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._logs_table.verticalHeader().setVisible(False)
        self._logs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._logs_table.setSelectionMode(QTableWidget.NoSelection)
        self._logs_table.setFixedHeight(220)

        layout.addWidget(lbl)
        layout.addWidget(self._logs_table)
        return frame

    def _build_pending_enrollments_frame(self) -> QFrame:
        """Construit l'encadré des demandes d'inscription en attente."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl = QLabel("Demandes en attente")
        lbl.setStyleSheet(
            f"font-weight: 600; font-size: 15px; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )

        self._enrollments_table = QTableWidget(0, 2)
        self._enrollments_table.setHorizontalHeaderLabels(["Nom", "Date"])
        self._enrollments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._enrollments_table.verticalHeader().setVisible(False)
        self._enrollments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._enrollments_table.setSelectionMode(QTableWidget.NoSelection)
        self._enrollments_table.setFixedHeight(220)

        layout.addWidget(lbl)
        layout.addWidget(self._enrollments_table)
        return frame

    def _refresh_logs_table(self) -> None:
        """Remplit le tableau des logs récents."""
        logs = self._log_service.get_recent_logs(limit=5)
        self._logs_table.setRowCount(len(logs))

        for row, log in enumerate(logs):
            self._logs_table.setRowHeight(row, 42)

            for col, text in enumerate([log.user_name, log.user_role]):
                item = QTableWidgetItem(text)
                item.setForeground(QColor(Colors.TEXT_PRIMARY))
                self._logs_table.setItem(row, col, item)

            # Badge statut
            badge_widget = QWidget()
            badge_layout = QHBoxLayout(badge_widget)
            badge_layout.setContentsMargins(4, 0, 4, 0)
            badge = StatusBadge(log.status)
            badge_layout.addWidget(badge)
            self._logs_table.setCellWidget(row, 2, badge_widget)

            time_item = QTableWidgetItem(log.timestamp.strftime("%H:%M"))
            time_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self._logs_table.setItem(row, 3, time_item)

    def _refresh_pending_table(self) -> None:
        """Remplit le tableau des demandes en attente."""
        reqs = self._enroll_service.get_pending_requests()
        self._enrollments_table.setRowCount(len(reqs))

        for row, req in enumerate(reqs):
            self._enrollments_table.setRowHeight(row, 42)

            name_item = QTableWidgetItem(req.name)
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))

            date_item = QTableWidgetItem(req.submitted_at.strftime("%d/%m %H:%M"))
            date_item.setForeground(QColor(Colors.TEXT_SECONDARY))

            self._enrollments_table.setItem(row, 0, name_item)
            self._enrollments_table.setItem(row, 1, date_item)
