# =============================================================================
# ui/admin/integrity_panel.py
# Panneau de vérification de l'intégrité des logs (tatouage numérique)
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from app.ui.components.role_badge import IntegrityBadge
from app.services.log_service import LogService
from app.resources.styles import Colors


class IntegrityPanel(QWidget):
    """
    Panneau de vérification d'intégrité des logs via tatouage numérique.

    Affiche :
    - Un résumé global (nb de logs intègres vs corrompus)
    - Un tableau détaillé avec le watermark de chaque log
    - Un bouton pour lancer la vérification complète

    POINT D'INTÉGRATION FUTUR :
        Le bouton "Lancer la vérification" appelera watermarking.verify_log()
        (module core/watermarking.py) pour chaque entrée en base.
        La badge verte/rouge reflètera le vrai résultat HMAC.
    """

    def __init__(self, log_service: LogService, parent=None):
        super().__init__(parent)
        self._log_service = log_service
        self._is_verifying = False
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

        # ── En-tête ────────────────────────────────────────────────────────
        lbl_title = QLabel("Vérification d'Intégrité")
        lbl_title.setStyleSheet(
            f"font-size: 27px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_sub = QLabel(
            "Vérifie que chaque log n'a pas été altéré depuis sa création "
            "en recalculant son empreinte HMAC-SHA256."
        )
        lbl_sub.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        lbl_sub.setWordWrap(True)

        # ── Explication du tatouage numérique ──────────────────────────────
        explain_box = QFrame()
        explain_box.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.ACCENT_PURPLE}12;
                border: 1px solid {Colors.ACCENT_PURPLE}44;
                border-radius: 8px;
            }}
        """)
        el = QVBoxLayout(explain_box)
        el.setContentsMargins(16, 14, 16, 14)
        lbl_explain = QLabel(
            "🔏  <b>Comment fonctionne le tatouage numérique ?</b><br>"
            "À chaque création de log, un HMAC-SHA256 est calculé sur les données "
            "(utilisateur, statut, timestamp) avec une clé secrète. "
            "Ce code est stocké avec le log. Lors de la vérification, le HMAC est "
            "recalculé et comparé. Toute différence indique une altération du log."
        )
        lbl_explain.setStyleSheet(
            f"color: {Colors.ACCENT_PURPLE}; font-size: 19px; background: transparent; line-height: 1.6;"
        )
        lbl_explain.setWordWrap(True)
        lbl_explain.setTextFormat(Qt.RichText)
        el.addWidget(lbl_explain)

        # ── Résumé statistique ─────────────────────────────────────────────
        self._summary_row = QHBoxLayout()
        self._summary_row.setSpacing(12)
        self._summary_cards = {}
        for key, label, color in [
            ("total",     "Logs analysés",  Colors.TEXT_SECONDARY),
            ("intact",    "Intègres  ✓",    Colors.ACCENT_GREEN),
            ("corrupted", "Corrompus ⚠",    Colors.ACCENT_RED),
        ]:
            card = QFrame()
            card.setFixedHeight(70)
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.BG_SECONDARY};
                    border: 1px solid {Colors.BORDER};
                    border-top: 3px solid {color};
                    border-radius: 8px;
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 10, 16, 10)
            lbl_n = QLabel("—")
            lbl_n.setStyleSheet(f"font-size: 31px; font-weight: 700; color: {color}; background: transparent;")
            lbl_l = QLabel(label)
            lbl_l.setStyleSheet(f"font-size: 18px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
            cl.addWidget(lbl_n)
            cl.addWidget(lbl_l)
            self._summary_cards[key] = lbl_n
            self._summary_row.addWidget(card)

        # ── Barre de progression ───────────────────────────────────────────
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(False)
        self._progress_bar.setFixedHeight(6)

        # ── Bouton lancer vérification ─────────────────────────────────────
        btn_row = QHBoxLayout()
        self._btn_verify = QPushButton("  🔍  Lancer la vérification complète")
        self._btn_verify.setFixedHeight(44)
        self._btn_verify.setFixedWidth(280)
        self._btn_verify.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PURPLE};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #a371f7; }}
            QPushButton:disabled {{ background-color: {Colors.BG_HOVER}; color: {Colors.TEXT_MUTED}; }}
        """)
        self._btn_verify.clicked.connect(self._run_verification)

        self._lbl_last_check = QLabel("Aucune vérification effectuée.")
        self._lbl_last_check.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )

        btn_row.addWidget(self._btn_verify)
        btn_row.addSpacing(16)
        btn_row.addWidget(self._lbl_last_check)
        btn_row.addStretch()

        # ── Tableau détaillé ───────────────────────────────────────────────
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels([
            "Log ID", "Utilisateur", "Statut", "Timestamp", "Intégrité"
        ])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self._table.verticalHeader().setVisible(False)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setStyleSheet(f"""
            QTableWidget {{ alternate-background-color: {Colors.BG_TERTIARY}; }}
        """)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        layout.addWidget(explain_box)
        layout.addLayout(self._summary_row)
        layout.addWidget(self._progress_bar)
        layout.addLayout(btn_row)
        layout.addWidget(self._table)

    def _run_verification(self) -> None:
        """
        Simule une vérification de l'intégrité de tous les logs.
        [FUTUR] Appelle watermarking.verify_log(log) pour chaque entrée.
        """
        self._btn_verify.setEnabled(False)
        self._btn_verify.setText("Vérification en cours...")
        self._progress_bar.setVisible(True)
        self._progress_bar.setValue(0)

        # Timer pour simuler une progression
        self._progress_value = 0
        self._verify_timer = QTimer()
        self._verify_timer.timeout.connect(self._step_progress)
        self._verify_timer.start(30)

    def _step_progress(self) -> None:
        """Avance la barre de progression et charge les résultats à 100%."""
        self._progress_value += 5
        self._progress_bar.setValue(self._progress_value)

        if self._progress_value >= 100:
            self._verify_timer.stop()
            self._load_results()
            self._btn_verify.setEnabled(True)
            self._btn_verify.setText("  🔍  Lancer la vérification complète")

    def _load_results(self) -> None:
        """Charge et affiche les résultats de vérification."""
        from datetime import datetime
        results = self._log_service.verify_all_integrity()

        total     = len(results)
        intact    = sum(1 for r in results if r["integrity"])
        corrupted = total - intact

        # Mise à jour des compteurs
        self._summary_cards["total"].setText(str(total))
        self._summary_cards["intact"].setText(str(intact))
        self._summary_cards["corrupted"].setText(str(corrupted))

        self._lbl_last_check.setText(
            f"Dernière vérification : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
        )

        # Remplissage du tableau
        self._table.setRowCount(total)
        for row, result in enumerate(results):
            self._table.setRowHeight(row, 46)

            # Log ID
            id_item = QTableWidgetItem(str(result["log_id"]))
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 0, id_item)

            # Utilisateur
            user_item = QTableWidgetItem(result["user"])
            user_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            self._table.setItem(row, 1, user_item)

            # Statut
            status_item = QTableWidgetItem(result["status"])
            status_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self._table.setItem(row, 2, status_item)

            # Timestamp
            ts = result["timestamp"]
            ts_item = QTableWidgetItem(ts.strftime("%d/%m/%Y %H:%M:%S"))
            ts_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self._table.setItem(row, 3, ts_item)

            # Badge intégrité
            badge_w = QWidget()
            bl = QHBoxLayout(badge_w)
            bl.setContentsMargins(6, 2, 6, 2)
            bl.addStretch()
            bl.addWidget(IntegrityBadge(result["integrity"]))
            bl.addStretch()
            self._table.setCellWidget(row, 4, badge_w)
