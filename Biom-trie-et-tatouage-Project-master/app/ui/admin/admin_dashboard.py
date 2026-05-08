# =============================================================================
# ui/admin/admin_dashboard.py
# Dashboard administrateur avec sidebar de navigation et panneaux internes
#
# Architecture :
#   - QHBoxLayout principal : sidebar gauche + zone de contenu droite
#   - La sidebar contient les boutons de navigation
#   - La zone de contenu est un QStackedWidget contenant tous les panneaux
#   - La barre supérieure affiche le titre de l'admin et un bouton logout
# =============================================================================

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from app.core.router import Router
from app.core.session import Session
from app.services.log_service import LogService
from app.services.alert_service import AlertService
from app.services.enrollment_service import EnrollmentService
from app.resources.styles import Colors

# Import des panneaux
from app.ui.admin.overview_panel            import OverviewPanel
from app.ui.admin.users_panel               import UsersPanel
from app.ui.admin.logs_panel                import LogsPanel
from app.ui.admin.alerts_panel              import AlertsPanel
from app.ui.admin.enrollment_requests_panel import EnrollmentRequestsPanel
from app.ui.admin.integrity_panel           import IntegrityPanel
from app.ui.admin.settings_panel            import SettingsPanel


# =============================================================================
# Bouton de navigation dans la sidebar
# =============================================================================
class SidebarButton(QPushButton):
    """
    Bouton de la sidebar avec icône et texte.
    Supporte un état actif/inactif visuellement distinct.
    """

    STYLE_NORMAL = f"""
        QPushButton {{
            background-color: transparent;
            color: {Colors.TEXT_SECONDARY};
            border: none;
            border-radius: 10px;
            text-align: left;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {Colors.BG_TERTIARY};
            color: {Colors.TEXT_PRIMARY};
        }}
    """

    STYLE_ACTIVE = f"""
        QPushButton {{
            background-color: #eff6ff;
            color: {Colors.ACCENT_BLUE};
            border: none;
            border-left: 3px solid {Colors.ACCENT_BLUE};
            border-radius: 0px;
            text-align: left;
            padding: 10px 16px 10px 13px;
            font-size: 14px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #dbeafe;
        }}
    """

    def __init__(self, icon: str, text: str, parent=None):
        super().__init__(f"  {icon}  {text}", parent)
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        """Met à jour le style selon l'état actif/inactif."""
        self.setStyleSheet(self.STYLE_ACTIVE if active else self.STYLE_NORMAL)


# =============================================================================
# Dashboard Admin principal
# =============================================================================
class AdminDashboard(QWidget):
    """
    Fenêtre principale du dashboard administrateur.
    Compose une sidebar de navigation et une zone de contenu à panneaux.
    """

    # Définition de la navigation de la sidebar
    NAV_ITEMS = [
        ("📊", "Vue d'ensemble",      "overview"),
        ("👥", "Utilisateurs",         "users"),
        ("📝", "Demandes d'inscription","enrollments"),
        ("📋", "Logs d'accès",          "logs"),
        ("🚨", "Alertes",               "alerts"),
        ("🔏", "Vérification intégrité","integrity"),
        ("⚙️", "Paramètres",            "settings"),
    ]

    def __init__(self, log_service: LogService,
                 enrollment_service: EnrollmentService,
                 alert_service: AlertService,
                 parent=None):
        super().__init__(parent)
        self._log_service    = log_service
        self._enroll_service = enrollment_service
        self._alert_service = alert_service
        self._nav_buttons    = {}   # clé: page_id -> SidebarButton
        self._setup_ui()

    def showEvent(self, event) -> None:
        """Rafraîchit le nom de l'admin et navigue vers 'overview' à chaque ouverture."""
        super().showEvent(event)
        user = Session.get_instance().current_user
        if user:
            self._lbl_admin_name.setText(user.name)
            self._lbl_admin_role.setText("Administrateur")
        self._navigate_to("overview")

    def _setup_ui(self) -> None:
        """Construit la structure principale : topbar + sidebar + contenu."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Barre supérieure (topbar) ──────────────────────────────────────
        topbar = self._build_topbar()

        # ── Corps : sidebar + contenu ──────────────────────────────────────
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        sidebar = self._build_sidebar()
        content_area = self._build_content_area()

        body_layout.addWidget(sidebar)
        body_layout.addWidget(content_area, stretch=1)

        root_layout.addWidget(topbar)
        root_layout.addLayout(body_layout)

        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

    def _build_topbar(self) -> QFrame:
        """Construit la barre supérieure du dashboard."""
        topbar = QFrame()
        topbar.setObjectName("admin_topbar")
        topbar.setFixedHeight(64)
        topbar.setStyleSheet(f"""
            QFrame#admin_topbar {{
                background-color: {Colors.BG_SECONDARY};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(14)

        # Logo + titre
        lbl_logo = QLabel("🔐")
        lbl_logo.setStyleSheet("font-size: 24px; background: transparent;")
        lbl_title = QLabel("SecurAccess")
        lbl_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; letter-spacing: -0.5px;"
        )
        lbl_dash = QLabel("Dashboard Admin")
        lbl_dash.setStyleSheet(
            f"font-size: 14px; font-weight: 400; color: {Colors.TEXT_MUTED}; background: transparent;"
        )

        # Séparateur vertical
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER}; border: none; max-width: 1px;")
        sep.setFixedHeight(28)

        # Infos admin connecté
        admin_info = QVBoxLayout()
        admin_info.setSpacing(0)
        self._lbl_admin_name = QLabel("—")
        self._lbl_admin_name.setStyleSheet(
            f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        self._lbl_admin_role = QLabel("Administrateur")
        self._lbl_admin_role.setStyleSheet(
            f"font-size: 12px; color: {Colors.ACCENT_BLUE}; font-weight: 500; background: transparent;"
        )
        admin_info.addWidget(self._lbl_admin_name)
        admin_info.addWidget(self._lbl_admin_role)

        # Bouton logout
        btn_logout = QPushButton("  ⏻  Déconnexion")
        btn_logout.setFixedHeight(36)
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 8px;
                font-size: 13px;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT_RED};
                color: {Colors.ACCENT_RED};
                background-color: #fef2f2;
            }}
        """)
        btn_logout.clicked.connect(self._logout)

        layout.addWidget(lbl_logo)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_dash)
        layout.addStretch()
        layout.addWidget(sep)
        layout.addSpacing(14)
        layout.addLayout(admin_info)
        layout.addSpacing(14)
        layout.addWidget(btn_logout)

        return topbar

    def _build_sidebar(self) -> QFrame:
        """Construit la sidebar de navigation."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {Colors.BG_SECONDARY};
                border-right: 1px solid {Colors.BORDER};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(2)

        # Label section
        lbl_nav = QLabel("NAVIGATION")
        lbl_nav.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; font-weight: 700; "
            f"letter-spacing: 1.5px; padding: 8px 16px 8px; background: transparent;"
        )

        layout.addWidget(lbl_nav)

        # Boutons de navigation
        for icon, label, page_id in self.NAV_ITEMS:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, pid=page_id: self._navigate_to(pid))
            self._nav_buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Label version en bas
        lbl_version = QLabel("SecurAccess v1.0")
        lbl_version.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 11px; padding: 8px 16px; background: transparent;"
        )
        layout.addWidget(lbl_version)

        return sidebar

    def _build_content_area(self) -> QStackedWidget:
        """Construit la zone de contenu principal avec tous les panneaux empilés."""
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

        # Instanciation de chaque panneau
        self._panels = {
            "overview":    OverviewPanel(self._log_service, self._enroll_service),
            "users":       UsersPanel(),
            "enrollments": EnrollmentRequestsPanel(self._enroll_service),
            "logs":        LogsPanel(self._log_service),
            "alerts":      AlertsPanel(self._alert_service),
            "integrity":   IntegrityPanel(self._log_service),
            "settings":    SettingsPanel(),
        }

        # Ajout de chaque panneau au stack dans l'ordre de la sidebar
        for _, _, page_id in self.NAV_ITEMS:
            self._stack.addWidget(self._panels[page_id])

        return self._stack

    def _navigate_to(self, page_id: str) -> None:
        """
        Change le panneau actif et met à jour le style des boutons sidebar.
        """
        # Mise à jour visuelle des boutons
        for pid, btn in self._nav_buttons.items():
            btn.set_active(pid == page_id)

        # Changement du panneau affiché
        if page_id in self._panels:
            self._stack.setCurrentWidget(self._panels[page_id])

    def _logout(self) -> None:
        """Déconnecte l'admin et retourne à la page de login."""
        Session.get_instance().logout()
        Router.get_instance().clear_history()
        Router.get_instance().navigate("login")
