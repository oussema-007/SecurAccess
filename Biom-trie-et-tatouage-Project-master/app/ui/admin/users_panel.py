# =============================================================================
# ui/admin/users_panel.py
# Panneau de gestion des utilisateurs
# =============================================================================

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from app.ui.components.role_badge import RoleBadge, StatusBadge
from app.models.user import Role
from app.resources.styles import Colors
from app.services.database_service import DatabaseService


class UsersPanel(QWidget):
    """
    Panneau de gestion des utilisateurs.
    Affiche la liste des utilisateurs enregistrés dans le système.
    [Futur] Actions : activer/désactiver, modifier le rôle, supprimer.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DatabaseService()
        self._setup_ui()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._load_users()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(18)
        self.setStyleSheet(f"background-color: {Colors.BG_PRIMARY};")

        # ── Titre + bouton Ajouter ─────────────────────────────────────────
        header_row = QHBoxLayout()

        lbl_block = QVBoxLayout()
        lbl_title = QLabel("Gestion des Utilisateurs")
        lbl_title.setStyleSheet(
            f"font-size: 27px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; background: transparent;"
        )
        lbl_sub = QLabel("Liste des identités enregistrées dans le système biométrique.")
        lbl_sub.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        lbl_block.addWidget(lbl_title)
        lbl_block.addWidget(lbl_sub)

        btn_add = QPushButton("  ＋  Ajouter un utilisateur")
        btn_add.setFixedHeight(40)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_GREEN};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 20px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background-color: #2ea043; }}
        """)
        # [Futur] Connecter à un dialogue d'ajout d'utilisateur

        header_row.addLayout(lbl_block)
        header_row.addStretch()
        header_row.addWidget(btn_add)

        # ── Compteur ───────────────────────────────────────────────────────
        self._lbl_count = QLabel()
        self._lbl_count.setStyleSheet(
            f"font-size: 19px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )

        # ── Tableau ────────────────────────────────────────────────────────
        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels([
            "ID", "Nom complet", "Email", "Rôle", "Statut", "Face ID", "Actions"
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

        layout.addLayout(header_row)
        layout.addWidget(self._lbl_count)
        layout.addWidget(self._table)

    def _load_users(self) -> None:
        """Charge les utilisateurs depuis SQLite."""
        rows = self._db.fetch_all(
            """
            SELECT id, full_name, email, role, is_active, face_id
            FROM users
            ORDER BY id ASC
            """
        )
        users = [
            {
                "id": int(row["id"]),
                "name": row["full_name"],
                "email": row["email"],
                "role": row["role"],
                "is_active": bool(row["is_active"]),
                "face_id": row["face_id"],
            }
            for row in rows
        ]
        self._lbl_count.setText(f"{len(users)} utilisateur(s) enregistré(s)")
        self._table.setRowCount(len(users))

        for row, user in enumerate(users):
            self._table.setRowHeight(row, 50)

            # ID
            id_item = QTableWidgetItem(str(user["id"]))
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            id_item.setTextAlignment(Qt.AlignCenter)
            self._table.setItem(row, 0, id_item)

            # Nom
            name_item = QTableWidgetItem(user["name"])
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            self._table.setItem(row, 1, name_item)

            # Email
            email_item = QTableWidgetItem(user["email"])
            email_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self._table.setItem(row, 2, email_item)

            # Rôle (badge)
            role_w = QWidget()
            rl = QHBoxLayout(role_w)
            rl.setContentsMargins(6, 2, 6, 2)
            rl.addStretch()
            role_map = {
                "admin": Role.ADMIN,
                "ultimate": Role.ULTIMATE,
                "pro": Role.PRO,
                "user": Role.USER,
                "unauthorized": Role.UNAUTHORIZED,
            }
            rl.addWidget(RoleBadge(role_map.get(user["role"], Role.UNKNOWN)))
            rl.addStretch()
            self._table.setCellWidget(row, 3, role_w)

            # Statut actif/inactif
            status_text = "Actif" if user["is_active"] else "Inactif"
            status_w = QWidget()
            sl = QHBoxLayout(status_w)
            sl.setContentsMargins(6, 2, 6, 2)
            sl.addStretch()
            sl.addWidget(StatusBadge("Autorisé" if user["is_active"] else "Refusé"))
            sl.addStretch()
            self._table.setCellWidget(row, 4, status_w)

            # Face ID
            fid_item = QTableWidgetItem(user["face_id"])
            fid_item.setForeground(QColor(Colors.TEXT_MUTED))
            self._table.setItem(row, 5, fid_item)

            # Actions
            action_w = QWidget()
            al = QHBoxLayout(action_w)
            al.setContentsMargins(6, 2, 6, 2)
            al.addStretch()

            btn_toggle = QPushButton()
            btn_toggle.setFixedHeight(30)
            if user["role"] == "unauthorized":
                btn_toggle.setText("Débloquer")
                btn_toggle.setStyleSheet(f"background-color: {Colors.ACCENT_GREEN}; color: white; border: none; border-radius: 6px; padding: 0 12px; font-weight: bold;")
                btn_toggle.clicked.connect(lambda checked, uid=user["id"]: self._toggle_user_status(uid, "user"))
            else:
                btn_toggle.setText("Bloquer")
                btn_toggle.setStyleSheet(f"background-color: {Colors.ACCENT_RED}; color: white; border: none; border-radius: 6px; padding: 0 12px; font-weight: bold;")
                btn_toggle.clicked.connect(lambda checked, uid=user["id"]: self._toggle_user_status(uid, "unauthorized"))

            al.addWidget(btn_toggle)
            al.addStretch()
            self._table.setCellWidget(row, 6, action_w)

    def _toggle_user_status(self, user_id: int, new_role: str) -> None:
        """Met à jour le rôle et le statut actif/inactif d'un utilisateur."""
        is_active = 1 if new_role != "unauthorized" else 0
        self._db.execute("UPDATE users SET role = ?, is_active = ? WHERE id = ?", (new_role, is_active, user_id))
        self._load_users()
