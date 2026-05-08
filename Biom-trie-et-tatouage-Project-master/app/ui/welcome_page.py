# =============================================================================
# ui/welcome_page.py
# Page d'accueil après authentification réussie
# =============================================================================

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from app.core.router import Router
from app.core.session import Session
from app.models.user import Role
from app.ui.components.role_badge import RoleBadge
from app.resources.styles import Colors
from app.ui.dialogs.restricted_feature_dialog import RestrictedFeatureDialog


# =============================================================================
# Carte de section (cliquable et gérant 3 états : autorisé, restreint, caché)
# =============================================================================
class SectionCard(QFrame):
    """
    Carte représentant une section de contenu.
    Visuellement, si le rôle est insuffisant, elle est atténuée.
    La carte est cliquable dans les deux cas.
    Elle émet un signal "clicked" en passant la section cliquée.
    """
    
    clicked = pyqtSignal(dict, bool)  # Emet: (section_dict, has_access)

    def __init__(self, section_data: dict, user_role: Role, parent=None):
        super().__init__(parent)
        self._section_data = section_data
        self.setFixedHeight(140)
        self.setCursor(Qt.PointingHandCursor)

        required_role = section_data["role"]
        from app.models.user import ROLE_HIERARCHY
        user_level     = ROLE_HIERARCHY.get(user_role, -1)
        required_level = ROLE_HIERARCHY.get(required_role, -1)
        self._has_access = user_level >= required_level

        if self._has_access:
            self._build_unlocked(required_role)
        else:
            self._build_locked(required_role)

    def mousePressEvent(self, event):
        """Intercepte le clic sur la carte."""
        super().mousePressEvent(event)
        self.clicked.emit(self._section_data, self._has_access)

    def _build_unlocked(self, required_role: Role) -> None:
        """Style normal."""
        from app.models.user import ROLE_COLORS
        accent = ROLE_COLORS.get(required_role, Colors.ACCENT_BLUE)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-left: 4px solid {accent};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border-color: {accent}88;
                border-left: 4px solid {accent};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top = QHBoxLayout()
        lbl_icon = QLabel(self._section_data["icon"])
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")
        lbl_title = QLabel(self._section_data["title"])
        lbl_title.setStyleSheet(
            f"font-weight: 600; font-size: 16px; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        top.addWidget(lbl_icon)
        top.addWidget(lbl_title)
        top.addStretch()

        lbl_desc = QLabel(self._section_data["desc"])
        lbl_desc.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; background: transparent;"
        )
        lbl_desc.setWordWrap(True)

        lbl_access = QLabel("✓ Accès autorisé")
        lbl_access.setStyleSheet(f"color: {accent}; font-size: 12px; font-weight: 600; background: transparent;")

        layout.addLayout(top)
        layout.addWidget(lbl_desc)
        layout.addStretch()
        layout.addWidget(lbl_access)

    def _build_locked(self, required_role: Role) -> None:
        """Style Upsell / Restreint."""
        from app.models.user import ROLE_LABELS, ROLE_COLORS
        accent = ROLE_COLORS.get(required_role, Colors.TEXT_MUTED)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_TERTIARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 14px;
            }}
            QFrame:hover {{
                border-color: {accent}55;
                background-color: {Colors.BG_SECONDARY};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top = QHBoxLayout()
        lbl_icon = QLabel(self._section_data["icon"])
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent;")
        lbl_title = QLabel(self._section_data["title"])
        lbl_title.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 16px; font-weight: 500; background: transparent;"
        )
        
        lbl_lock = QLabel("🔒")
        lbl_lock.setStyleSheet("font-size: 16px; background: transparent;")
        
        top.addWidget(lbl_icon)
        top.addWidget(lbl_title)
        top.addStretch()
        top.addWidget(lbl_lock)

        lbl_desc = QLabel(self._section_data["desc"])
        lbl_desc.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        lbl_desc.setWordWrap(True)

        required_label = ROLE_LABELS.get(required_role, "Inconnu")
        lbl_req = QLabel(f"Disponible avec {required_label.upper()}")
        lbl_req.setStyleSheet(
            f"color: {accent}; font-size: 12px; font-weight: 600; background: transparent;"
        )

        layout.addLayout(top)
        layout.addWidget(lbl_desc)
        layout.addStretch()
        layout.addWidget(lbl_req)


# =============================================================================
# Page de bienvenue principale
# =============================================================================
class WelcomePage(QWidget):
    """
    Affiche la page de bienvenue après authentification.
    Les sections sont conditionnellement visibles (ou grisées) selon le rôle.
    """

    # Liste des sections avec leur rôle requis
    SECTIONS = [
        {"title": "Tableau de bord", "desc": "Vue d'ensemble de votre activité.", "icon": "📊", "role": Role.USER, "visible_by_roles": [Role.USER, Role.PRO, Role.ULTIMATE, Role.ADMIN]},
        {"title": "Messages", "desc": "Consultez vos messages internes.", "icon": "💬", "role": Role.USER, "visible_by_roles": [Role.USER, Role.PRO, Role.ULTIMATE, Role.ADMIN]},
        {"title": "Rapports Pro", "desc": "Accédez aux rapports analytiques avancés.", "icon": "📈", "role": Role.PRO, "visible_by_roles": [Role.USER, Role.PRO, Role.ULTIMATE, Role.ADMIN]},
        {"title": "Outils Pro", "desc": "Suite d'outils professionnels exclusifs.", "icon": "🛠", "role": Role.PRO, "visible_by_roles": [Role.USER, Role.PRO, Role.ULTIMATE, Role.ADMIN]},
        {"title": "Espace Ultimate", "desc": "Fonctionnalités exclusives Ultimate.", "icon": "⭐", "role": Role.ULTIMATE, "visible_by_roles": [Role.PRO, Role.ULTIMATE, Role.ADMIN]},
        {"title": "API & Intégrations", "desc": "Gérez les connexions aux systèmes tiers.", "icon": "🔗", "role": Role.ULTIMATE, "visible_by_roles": [Role.PRO, Role.ULTIMATE, Role.ADMIN]},
        {"title": "Administration", "desc": "Gestion complète du système.", "icon": "⚙️", "role": Role.ADMIN, "visible_by_roles": [Role.ADMIN]},
        {"title": "Sécurité & Logs", "desc": "Audit de sécurité et logs d'accès.", "icon": "🔐", "role": Role.ADMIN, "visible_by_roles": [Role.ADMIN]},
    ]

    def __init__(self, log_service=None, upgrade_service=None, parent=None):
        super().__init__(parent)
        self._log_service = log_service
        self._upgrade_service = upgrade_service
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_clock)
        self._setup_ui()

    def set_services(self, log_service, upgrade_service) -> None:
        """Injecte les services (parfois fait après init)."""
        self._log_service = log_service
        self._upgrade_service = upgrade_service

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._refresh_content()
        self._timer.start(1000)

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self._timer.stop()

    def _setup_ui(self) -> None:
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)

        self._topbar = self._build_topbar()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._content_widget = QWidget()
        self._content_widget.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(40, 30, 40, 40)
        self._content_layout.setSpacing(28)

        scroll.setWidget(self._content_widget)
        self._main_layout.addWidget(self._topbar)
        self._main_layout.addWidget(scroll)

    def _build_topbar(self) -> QFrame:
        topbar = QFrame()
        topbar.setFixedHeight(64)
        topbar.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border-bottom: 1px solid {Colors.BORDER};
            }}
        """)
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 0, 24, 0)
        
        lbl_logo = QLabel("🔐 SecurAccess")
        lbl_logo.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; letter-spacing: -0.5px;"
        )
        self._lbl_clock = QLabel()
        self._lbl_clock.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        self._update_clock()

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
        layout.addStretch()
        layout.addWidget(self._lbl_clock)
        layout.addSpacing(12)
        layout.addWidget(btn_logout)
        return topbar

    def _refresh_content(self) -> None:
        session = Session.get_instance()
        user = session.current_user
        if not user:
            return

        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._content_layout.addWidget(self._build_welcome_header(user))

        lbl_sections = QLabel("Mes sections")
        lbl_sections.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; letter-spacing: -0.5px;"
        )
        self._content_layout.addWidget(lbl_sections)

        grid = QGridLayout()
        grid.setSpacing(16)

        visible_count = 0
        for section in self.SECTIONS:
            # Ne montre la carte que si le rôle de l'utilisateur est dans la liste "visible_by_roles"
            if user.role in section["visible_by_roles"] or user.role == Role.ADMIN:
                card = SectionCard(section_data=section, user_role=user.role)
                card.clicked.connect(self._handle_card_click)
                grid.addWidget(card, visible_count // 2, visible_count % 2)
                visible_count += 1

        self._content_layout.addLayout(grid)
        self._content_layout.addStretch()

    def _build_welcome_header(self, user) -> QFrame:
        """Construit l'en-tête de bienvenue."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        lbl_avatar = QLabel("👤")
        lbl_avatar.setStyleSheet(f"""
            font-size: 49px; background-color: {Colors.BG_TERTIARY}; 
            border-radius: 30px; padding: 8px;
        """)
        lbl_avatar.setFixedSize(64, 64)
        lbl_avatar.setAlignment(Qt.AlignCenter)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(6)
        lbl_welcome = QLabel(f"Bienvenue, {user.name} 👋")
        lbl_welcome.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent; letter-spacing: -0.5px;"
        )

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(RoleBadge(user.role))
        lbl_email = QLabel(user.email)
        lbl_email.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; background: transparent;")
        row.addWidget(lbl_email)
        row.addStretch()

        text_layout.addWidget(lbl_welcome)
        text_layout.addLayout(row)

        layout.addWidget(lbl_avatar)
        layout.addLayout(text_layout)
        layout.addStretch()
        return frame

    def _handle_card_click(self, section: dict, has_access: bool) -> None:
        """Gère le clic sur une carte de section (autorisée ou restreinte)."""
        user = Session.get_instance().current_user
        if not user:
            return

        if has_access:
            # Action classique (ex: un QMessageBox ou un Print pour l'instant)
            QMessageBox.information(self, "Accès fonctionnel", f"Ouverture de : {section['title']}")
            return

        # ---- L'accès est restreint ----
        
        # 1. Logger la tentative
        if self._log_service:
            self._log_service.add_action_log(
                user_name=user.name, 
                user_role=user.role_label, 
                action_type="RESTRICTED_ACCESS",
                details=f"Tentative d'accès à '{section['title']}' (Requiert: {section['role'].name})"
            )
            self._log_service.add_action_log(
                user_name=user.name,
                user_role=user.role_label,
                action_type="UPGRADE_PROMPT_SHOWN",
                details=f"Prompt d'évolution affiché pour '{section['title']}'"
            )

        # 2. Ouvrir le dialogue de restriction
        dialog = RestrictedFeatureDialog(
            feature_name=section['title'], 
            required_role=section['role'], 
            current_role=user.role, 
            parent=self
        )
        result = dialog.exec_()

        # 3. Traiter le choix de l'utilisateur
        if result == RestrictedFeatureDialog.CHOICE_UPGRADE_REQUEST:
            if self._log_service:
                self._log_service.add_action_log(
                    user_name=user.name,
                    user_role=user.role_label,
                    action_type="UPGRADE_REQUEST",
                    details=f"Demande d'upgrade vers {section['role'].name} envoyée"
                )
            if self._upgrade_service:
                self._upgrade_service.submit_upgrade_request(user, section['role'], section['title'])

            QMessageBox.information(
                self, 
                "Demande envoyée", 
                f"Votre demande d'évolution pour débloquer '{section['title']}' a bien été enregistrée et sera traitée par un administrateur."
            )

    def _update_clock(self) -> None:
        self._lbl_clock.setText(datetime.now().strftime("%A %d %B %Y — %H:%M:%S"))

    def _logout(self) -> None:
        Session.get_instance().logout()
        Router.get_instance().clear_history()
        Router.get_instance().navigate("login")
