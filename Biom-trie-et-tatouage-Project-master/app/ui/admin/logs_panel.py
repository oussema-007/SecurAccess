# =============================================================================
# ui/admin/logs_panel.py
# Panneau de consultation des logs d'accès
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import re

from app.ui.components.role_badge import StatusBadge, IntegrityBadge
from app.services.log_service import LogService
from app.resources.styles import Colors


class LogsPanel(QWidget):
    """
    Panneau de consultation de l'historique des accès.
    Affiche tous les logs avec possibilité de filtrer par nom.
    Chaque log affiche son badge d'intégrité (tatouage numérique).
    """

    def __init__(self, log_service: LogService, parent=None):
        super().__init__(parent)
        self._log_service = log_service
        self._setup_ui()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._load_logs()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

        # ── Titre ──────────────────────────────────────────────────────────
        lbl_title = QLabel("Historique des accès")
        lbl_title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; letter-spacing: -0.5px;"
        )
        lbl_sub = QLabel("Tous les événements d'authentification du système.")
        lbl_sub.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )

        # ── Barre de filtres ───────────────────────────────────────────────
        filter_row = QHBoxLayout()
        filter_row.setSpacing(12)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍  Rechercher par nom...")
        self._search_input.setFixedHeight(38)
        self._search_input.textChanged.connect(self._load_logs)

        btn_refresh = QPushButton("↻  Actualiser")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setFixedWidth(130)
        btn_refresh.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.BG_SECONDARY};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background-color: {Colors.BG_TERTIARY}; border-color: {Colors.ACCENT_BLUE}; }}
        """)
        btn_refresh.clicked.connect(self._load_logs)

        filter_row.addWidget(self._search_input)
        filter_row.addWidget(btn_refresh)

        # Note sur le tatouage
        info_box = QFrame()
        info_box.setStyleSheet(f"""
            QFrame {{
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 10px;
            }}
        """)
        info_layout = QHBoxLayout(info_box)
        info_layout.setContentsMargins(14, 10, 14, 10)
        lbl_info = QLabel(
            "🔏  Chaque log est signé par un tatouage numérique (HMAC-SHA256). "
            "La colonne 'Intégrité' indique si le log n'a pas été altéré."
        )
        lbl_info.setStyleSheet(
            f"color: {Colors.ACCENT_BLUE}; font-size: 12px; background: transparent;"
        )
        lbl_info.setWordWrap(True)
        info_layout.addWidget(lbl_info)

        # ── Tableau des logs ───────────────────────────────────────────────
        self._table = QTableWidget(0, 8)
        self._table.setHorizontalHeaderLabels([
            "ID", "Utilisateur", "Rôle", "Statut", "Confiance", "Score distance", "Date / Heure", "Intégrité"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                alternate-background-color: {Colors.BG_TERTIARY};
            }}
        """)

        # Assemblage
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        layout.addLayout(filter_row)
        layout.addWidget(info_box)
        layout.addWidget(self._table)

    def _load_logs(self) -> None:
        """Charge et filtre les logs depuis le service."""
        search = self._search_input.text().strip().lower()
        logs   = self._log_service.get_recent_logs(limit=50)

        # Filtrage par texte si nécessaire
        if search:
            logs = [l for l in logs if search in l.user_name.lower() or search in l.user_role.lower()]

        self._table.setRowCount(len(logs))

        for row, log in enumerate(logs):
            self._table.setRowHeight(row, 46)

            # Determine row background color based on status
            row_bg = None
            status_lower = log.status.lower() if log.status else ""
            if status_lower in ("autorisé", "admin"):
                row_bg = QColor(34, 197, 94, 18)    # Green tint
            elif status_lower == "refusé":
                row_bg = QColor(239, 68, 68, 18)     # Red tint
            elif status_lower == "inconnu":
                row_bg = QColor(245, 158, 11, 18)    # Orange tint

            # ID
            id_item = QTableWidgetItem(str(log.id))
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            id_item.setTextAlignment(Qt.AlignCenter)
            if row_bg:
                id_item.setBackground(row_bg)
            self._table.setItem(row, 0, id_item)

            # Nom
            name_item = QTableWidgetItem(log.user_name)
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            if row_bg:
                name_item.setBackground(row_bg)
            self._table.setItem(row, 1, name_item)

            # Rôle
            role_item = QTableWidgetItem(log.user_role)
            role_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            if row_bg:
                role_item.setBackground(row_bg)
            self._table.setItem(row, 2, role_item)

            # Statut (badge)
            badge_w = QWidget()
            bl = QHBoxLayout(badge_w)
            bl.setContentsMargins(6, 2, 6, 2)
            bl.addStretch()
            bl.addWidget(StatusBadge(log.status))
            bl.addStretch()
            self._table.setCellWidget(row, 3, badge_w)

            # Confiance
            conf_item = QTableWidgetItem(f"{log.confidence * 100:.0f}%")
            conf_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            conf_item.setTextAlignment(Qt.AlignCenter)
            if row_bg:
                conf_item.setBackground(row_bg)
            self._table.setItem(row, 4, conf_item)

            # Score distance extrait du champ details
            score_item = QTableWidgetItem(self._extract_distance_score(log.details))
            score_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            score_item.setTextAlignment(Qt.AlignCenter)
            if row_bg:
                score_item.setBackground(row_bg)
            self._table.setItem(row, 5, score_item)

            # Timestamp
            ts_item = QTableWidgetItem(log.timestamp.strftime("%d/%m/%Y  %H:%M:%S"))
            ts_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            if row_bg:
                ts_item.setBackground(row_bg)
            self._table.setItem(row, 6, ts_item)

            # Intégrité (badge)
            int_w = QWidget()
            il = QHBoxLayout(int_w)
            il.setContentsMargins(6, 2, 6, 2)
            il.addStretch()
            il.addWidget(IntegrityBadge(log.integrity_ok))
            il.addStretch()
            self._table.setCellWidget(row, 7, int_w)

    def _extract_distance_score(self, details: str) -> str:
        """Extrait score_distance depuis le texte de details."""
        if not details:
            return "NA"
        match = re.search(r"score_distance=([0-9]+(?:\.[0-9]+)?)", details)
        if not match:
            return "NA"
        return match.group(1)
