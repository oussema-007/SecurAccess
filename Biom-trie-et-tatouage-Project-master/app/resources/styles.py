# =============================================================================
# resources/styles.py
# Système de design moderne — Light SaaS Theme
#
# Palette inspirée : off-white, clean white cards, deep slate text,
# muted blue-gray secondaire, accents navy-teal.
# Typographie : Inter (fallback Segoe UI)
# =============================================================================


class Colors:
    """
    Palette de couleurs centralisée.
    Toutes les pages et composants référencent cette classe.
    """

    # ── Fonds ──────────────────────────────────────────────────────────────
    BG_PRIMARY   = "#f8fafc"   # Off-white chaud — fond global
    BG_SECONDARY = "#ffffff"   # Blanc pur — cartes, panneaux
    BG_TERTIARY  = "#f1f5f9"   # Gris très léger — inputs, zones secondaires
    BG_HOVER     = "#e2e8f0"   # Hover léger

    # ── Texte ──────────────────────────────────────────────────────────────
    TEXT_PRIMARY   = "#1e2a3e"  # Slate profond
    TEXT_SECONDARY = "#5b6e8c"  # Bleu-gris doux
    TEXT_MUTED     = "#94a3b8"  # Encore plus léger

    # ── Accents ────────────────────────────────────────────────────────────
    ACCENT_BLUE   = "#3b82f6"   # Bleu moderne interactif
    ACCENT_GREEN  = "#22c55e"   # Vert succès
    ACCENT_RED    = "#ef4444"   # Rouge erreur
    ACCENT_ORANGE = "#f59e0b"   # Orange avertissement
    ACCENT_PURPLE = "#8b5cf6"   # Violet premium
    ACCENT_TEAL   = "#06b6d4"   # Teal info

    # ── Bordures ───────────────────────────────────────────────────────────
    BORDER       = "#e2e8f0"    # Bordure très discrète
    BORDER_FOCUS = "#3b82f6"    # Bordure focus = accent bleu


# =============================================================================
# Feuille de style globale — appliquée via app.setStyleSheet()
# =============================================================================
MAIN_STYLESHEET = f"""
/* ── FENÊTRE PRINCIPALE ─────────────────────────────────────────────────── */
QMainWindow, QDialog {{
    background-color: {Colors.BG_PRIMARY};
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}}

QWidget {{
    background-color: transparent;
    color: {Colors.TEXT_PRIMARY};
    font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
}}

/* ── LABELS ─────────────────────────────────────────────────────────────── */
QLabel {{
    color: {Colors.TEXT_PRIMARY};
    background: transparent;
}}

/* ── BOUTONS ────────────────────────────────────────────────────────────── */
QPushButton {{
    background-color: {Colors.BG_SECONDARY};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    padding: 8px 20px;
    font-size: 14px;
    font-weight: 500;
    min-height: 36px;
}}
QPushButton:hover {{
    background-color: {Colors.BG_TERTIARY};
    border-color: {Colors.ACCENT_BLUE};
    color: {Colors.ACCENT_BLUE};
}}
QPushButton:pressed {{
    background-color: {Colors.BG_HOVER};
}}
QPushButton:disabled {{
    color: {Colors.TEXT_MUTED};
    border-color: {Colors.BORDER};
    background-color: {Colors.BG_TERTIARY};
}}

/* ── BOUTON PRINCIPAL (accent) ──────────────────────────────────────────── */
QPushButton#btn_primary {{
    background-color: {Colors.ACCENT_BLUE};
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    padding: 10px 24px;
}}
QPushButton#btn_primary:hover {{
    background-color: #2563eb;
    color: white;
}}
QPushButton#btn_primary:pressed {{
    background-color: #1d4ed8;
}}
QPushButton#btn_primary:disabled {{
    background-color: #93c5fd;
    color: white;
}}

/* ── CHAMPS TEXTE ───────────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {Colors.BG_SECONDARY};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 14px;
    selection-background-color: {Colors.ACCENT_BLUE};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {Colors.BORDER_FOCUS};
    background-color: {Colors.BG_SECONDARY};
}}
QLineEdit::placeholder {{
    color: {Colors.TEXT_MUTED};
}}

/* ── COMBO / SPIN ───────────────────────────────────────────────────────── */
QComboBox, QSpinBox {{
    background-color: {Colors.BG_SECONDARY};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 14px;
}}
QComboBox:hover, QSpinBox:hover {{
    border-color: {Colors.ACCENT_BLUE};
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}

/* ── TABLEAU ────────────────────────────────────────────────────────────── */
QTableWidget {{
    background-color: {Colors.BG_SECONDARY};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER};
    border-radius: 12px;
    gridline-color: {Colors.BORDER};
    font-size: 13px;
    selection-background-color: #dbeafe;
    selection-color: {Colors.TEXT_PRIMARY};
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {Colors.BORDER};
}}
QHeaderView::section {{
    background-color: {Colors.BG_TERTIARY};
    color: {Colors.TEXT_SECONDARY};
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid {Colors.BORDER};
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── SCROLLBAR ──────────────────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background-color: {Colors.BORDER};
    min-height: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {Colors.TEXT_MUTED};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 2px 4px;
}}
QScrollBar::handle:horizontal {{
    background-color: {Colors.BORDER};
    min-width: 30px;
    border-radius: 4px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ── TOOLTIP ────────────────────────────────────────────────────────────── */
QToolTip {{
    background-color: {Colors.TEXT_PRIMARY};
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}

/* ── CHECKBOX ───────────────────────────────────────────────────────────── */
QCheckBox {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 14px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {Colors.BORDER};
    border-radius: 4px;
    background-color: {Colors.BG_SECONDARY};
}}
QCheckBox::indicator:checked {{
    background-color: {Colors.ACCENT_BLUE};
    border-color: {Colors.ACCENT_BLUE};
}}
QCheckBox::indicator:hover {{
    border-color: {Colors.ACCENT_BLUE};
}}

/* ── TAB WIDGET ──────────────────────────────────────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    background-color: {Colors.BG_SECONDARY};
}}
QTabBar::tab {{
    background-color: {Colors.BG_TERTIARY};
    color: {Colors.TEXT_SECONDARY};
    padding: 8px 18px;
    border: 1px solid {Colors.BORDER};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-size: 13px;
    font-weight: 500;
}}
QTabBar::tab:selected {{
    background-color: {Colors.BG_SECONDARY};
    color: {Colors.ACCENT_BLUE};
    border-color: {Colors.BORDER};
    font-weight: 600;
}}
QTabBar::tab:hover {{
    color: {Colors.ACCENT_BLUE};
}}

/* ── MESSAGE BOX ─────────────────────────────────────────────────────────── */
QMessageBox {{
    background-color: {Colors.BG_SECONDARY};
}}
QMessageBox QLabel {{
    color: {Colors.TEXT_PRIMARY};
    font-size: 14px;
}}
"""

# =============================================================================
# Styles spécifiques aux zones de scan (login page)
# =============================================================================
SCAN_STATUS_IDLE    = f"color: {Colors.TEXT_SECONDARY}; font-size: 14px;"
SCAN_STATUS_LOADING = f"color: {Colors.ACCENT_BLUE}; font-size: 14px; font-weight: 600;"
SCAN_STATUS_SUCCESS = f"color: {Colors.ACCENT_GREEN}; font-size: 14px; font-weight: 600;"
SCAN_STATUS_ERROR   = f"color: {Colors.ACCENT_RED}; font-size: 14px; font-weight: 600;"
