# =============================================================================
# ui/admin/alerts_panel.py
# Panneau des alertes de sécurité
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton
)
from PyQt5.QtCore import Qt
from app.resources.styles import Colors
from app.services.alert_service import AlertService, SecurityAlert


# ── Widget carte d'alerte ─────────────────────────────────────────────────────
class AlertCard(QFrame):
    """Carte représentant une alerte individuelle."""

    def __init__(self, alert: SecurityAlert, parent=None):
        super().__init__(parent)
        color = self._level_color(alert.level)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-left: 4px solid {color};
                border-radius: 8px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(14)

        # Icône niveau
        lbl_icon = QLabel(self._level_icon(alert.level))
        lbl_icon.setStyleSheet(f"font-size: 29px; background: transparent;")
        lbl_icon.setFixedWidth(30)
        lbl_icon.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # Contenu texte
        content = QVBoxLayout()
        content.setSpacing(4)

        # Ligne titre + badge niveau
        title_row = QHBoxLayout()
        lbl_title = QLabel(alert.title)
        lbl_title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_badge = QLabel(self._level_label(alert.level))
        lbl_badge.setStyleSheet(f"""
            color: {color};
            font-size: 17px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 8px;
            background-color: {color}22;
            border: 1px solid {color}55;
        """)
        title_row.addWidget(lbl_title)
        title_row.addWidget(lbl_badge)
        title_row.addStretch()

        lbl_msg = QLabel(alert.message)
        lbl_msg.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        lbl_msg.setWordWrap(True)

        lbl_time = QLabel(alert.timestamp.strftime("%d/%m/%Y à %H:%M"))
        lbl_time.setStyleSheet(
            f"font-size: 18px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )

        content.addLayout(title_row)
        content.addWidget(lbl_msg)
        content.addWidget(lbl_time)

        layout.addWidget(lbl_icon)
        layout.addLayout(content)

    @staticmethod
    def _level_color(level: str) -> str:
        return {
            "critical": Colors.ACCENT_RED,
            "warning": Colors.ACCENT_ORANGE,
            "info": Colors.ACCENT_BLUE,
        }.get(level, Colors.TEXT_SECONDARY)

    @staticmethod
    def _level_icon(level: str) -> str:
        return {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️",
        }.get(level, "•")

    @staticmethod
    def _level_label(level: str) -> str:
        return {
            "critical": "CRITIQUE",
            "warning": "AVERTISSEMENT",
            "info": "INFO",
        }.get(level, level.upper())


# ── Panneau principal ─────────────────────────────────────────────────────────
class AlertsPanel(QWidget):
    """
    Panneau des alertes de sécurité.
    [Futur] Les alertes seront générées automatiquement depuis le moteur de règles
    (x tentatives échouées, score de confiance trop faible, etc.)
    """

    def __init__(self, alert_service: AlertService, parent=None):
        super().__init__(parent)
        self._alert_service = alert_service
        self._setup_ui()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._filter_alerts("all")

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

        # ── En-tête ────────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        lbl_block = QVBoxLayout()

        lbl_title = QLabel("Alertes de Sécurité")
        lbl_title.setStyleSheet(
            f"font-size: 27px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_sub = QLabel("Événements anormaux détectés par le système de surveillance.")
        lbl_sub.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        lbl_block.addWidget(lbl_title)
        lbl_block.addWidget(lbl_sub)

        # Filtres rapides
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        for level, label, color in [
            ("all",      "Toutes",          Colors.TEXT_SECONDARY),
            ("critical", "Critiques 🚨",    Colors.ACCENT_RED),
            ("warning",  "Avertissements ⚠️", Colors.ACCENT_ORANGE),
            ("info",     "Infos ℹ️",         Colors.ACCENT_BLUE),
        ]:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}22;
                    color: {color};
                    border: 1px solid {color}55;
                    border-radius: 6px;
                    font-size: 18px;
                    font-weight: 600;
                    padding: 0 12px;
                }}
                QPushButton:hover {{ background-color: {color}44; }}
            """)
            btn.clicked.connect(lambda checked, lv=level: self._filter_alerts(lv))
            filter_row.addWidget(btn)
        filter_row.addStretch()

        header_row.addLayout(lbl_block)
        header_row.addStretch()

        # ── Compteurs résumés ──────────────────────────────────────────────
        counts = self._alert_service.get_counts()
        critical_count = counts["critical"]
        warning_count = counts["warning"]

        summary_row = QHBoxLayout()
        summary_row.setSpacing(12)
        for count, label, color in [
            (critical_count, "Critiques",       Colors.ACCENT_RED),
            (warning_count,  "Avertissements",  Colors.ACCENT_ORANGE),
            (counts["total"], "Total alertes", Colors.TEXT_SECONDARY),
        ]:
            card = QFrame()
            card.setFixedHeight(56)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.BG_SECONDARY};
                    border: 1px solid {Colors.BORDER};
                    border-left: 3px solid {color};
                    border-radius: 8px;
                }}
            """)
            cl = QHBoxLayout(card)
            cl.setContentsMargins(14, 0, 14, 0)
            lbl_n = QLabel(str(count))
            lbl_n.setStyleSheet(f"font-size: 29px; font-weight: 700; color: {color}; background: transparent;")
            lbl_l = QLabel(label)
            lbl_l.setStyleSheet(f"font-size: 18px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
            cl.addWidget(lbl_n)
            cl.addWidget(lbl_l)
            summary_row.addWidget(card)

        # ── Liste scrollable des alertes ───────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._alerts_container = QWidget()
        self._alerts_container.setStyleSheet("background: transparent;")
        self._alerts_layout = QVBoxLayout(self._alerts_container)
        self._alerts_layout.setContentsMargins(0, 0, 0, 0)
        self._alerts_layout.setSpacing(10)

        scroll.setWidget(self._alerts_container)

        # Chargement initial
        self._filter_alerts("all")

        layout.addLayout(header_row)
        layout.addLayout(filter_row)
        layout.addLayout(summary_row)
        layout.addWidget(scroll)

    def _filter_alerts(self, level: str) -> None:
        """Filtre et affiche les alertes selon le niveau sélectionné."""
        # Vider la liste précédente
        while self._alerts_layout.count():
            item = self._alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Filtrer
        all_alerts = self._alert_service.get_recent_alerts(limit=100)
        filtered = all_alerts if level == "all" else [a for a in all_alerts if a.level == level]

        if not filtered:
            lbl_empty = QLabel("Aucune alerte dans cette catégorie.")
            lbl_empty.setStyleSheet(
                f"color: {Colors.TEXT_MUTED}; font-size: 20px; background: transparent;"
            )
            lbl_empty.setAlignment(Qt.AlignCenter)
            self._alerts_layout.addWidget(lbl_empty)
        else:
            for alert in sorted(filtered, key=lambda a: a.timestamp, reverse=True):
                self._alerts_layout.addWidget(AlertCard(alert))

        self._alerts_layout.addStretch()
