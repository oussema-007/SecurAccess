# =============================================================================
# ui/login_page.py
# Page de connexion par reconnaissance faciale
#
# Flux :
#   1. L'utilisateur clique "Scanner mon visage"
#   2. Un loader anime l'attente (QTimer)
#   3. Le service d'authentification est appelé
#   4. Selon le résultat, on navigue vers la bonne page
#
# Mode développeur :
#   Un panneau repliable en bas permet de sélectionner un face_id de test
#   sans caméra. Ce panneau est clairement visible et désactivable.
# =============================================================================

import cv2
import numpy as np
from PyQt5.QtCore import QThread, QTimer, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsDropShadowEffect

from app.controllers.auth_controller import AuthController
from app.models.auth_result import AuthStatus
from app.resources.styles import (
    Colors,
    SCAN_STATUS_ERROR,
    SCAN_STATUS_IDLE,
    SCAN_STATUS_LOADING,
    SCAN_STATUS_SUCCESS,
)
from app.services.camera_service import CameraService


class ScanWorker(QThread):
    """Thread dedie a l'analyse pour eviter de figer l'interface."""

    finished = pyqtSignal(object)

    def __init__(self, auth_controller: AuthController, frame):
        super().__init__()
        self._auth_controller = auth_controller
        self._frame = frame.copy()

    def run(self) -> None:
        result = self._auth_controller.authenticate_frame(self._frame)
        self.finished.emit(result)


class LoginPage(QWidget):
    """Page de login connectee a la vraie webcam."""

    def __init__(self, camera_service: CameraService, auth_controller: AuthController, parent=None):
        super().__init__(parent)
        self._camera_service = camera_service
        self._auth_controller = auth_controller
        self._worker = None
        self._current_frame = None
        self._is_scanning = False
        self._scan_pulse_step = 0
        # Haar cascade for real-time face overlay
        self._face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self._camera_timer = QTimer(self)
        self._camera_timer.timeout.connect(self._refresh_camera)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("login_card")
        card.setFixedWidth(720)
        card.setStyleSheet(
            f"""
            QFrame#login_card {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 24px;
            }}
            """
        )
        # Subtle drop shadow on the card
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 18))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(16)

        # Title with icon
        title = QLabel("🔐  Connexion biométrique")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;")

        subtitle = QLabel("Positionnez votre visage face à la caméra")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 14px; font-weight: 400;")

        self._camera_label = QLabel("Initialisation camera...")
        self._camera_label.setAlignment(Qt.AlignCenter)
        self._camera_label.setFixedSize(640, 360)
        self._camera_label.setObjectName("camera_view")
        self._camera_label.setStyleSheet(
            f"background-color: {Colors.BG_TERTIARY}; border: 2px solid {Colors.BORDER}; border-radius: 12px;"
        )

        self._status_label = QLabel("Camera en cours d'initialisation...")
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setWordWrap(True)
        self._status_label.setStyleSheet(SCAN_STATUS_IDLE)

        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        self._scan_button = QPushButton("⎋  Scanner mon visage")
        self._scan_button.setObjectName("btn_primary")
        self._scan_button.setFixedHeight(46)
        self._scan_button.setCursor(Qt.PointingHandCursor)
        self._scan_button.clicked.connect(self._on_scan_clicked)
        # Glow effect on scan button
        scan_glow = QGraphicsDropShadowEffect()
        scan_glow.setBlurRadius(24)
        scan_glow.setOffset(0, 4)
        scan_glow.setColor(QColor(59, 130, 246, 80))
        self._scan_button.setGraphicsEffect(scan_glow)

        self._retry_button = QPushButton("↻  Réessayer")
        self._retry_button.setFixedHeight(46)
        self._retry_button.setCursor(Qt.PointingHandCursor)
        self._retry_button.clicked.connect(self._set_ready_state)

        buttons.addWidget(self._scan_button)
        buttons.addWidget(self._retry_button)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self._camera_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(self._status_label)
        card_layout.addLayout(buttons)
        layout.addWidget(card)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._start_camera()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self._stop_camera()

    def closeEvent(self, event) -> None:
        self._stop_camera()
        super().closeEvent(event)

    def _start_camera(self) -> None:
        """Demarre la webcam et le rafraichissement."""
        if self._camera_service.start():
            self._status_label.setText("Camera active. Positionnez votre visage puis scannez.")
            self._status_label.setStyleSheet(SCAN_STATUS_IDLE)
            self._camera_timer.start(33)
        else:
            self._status_label.setText("Camera indisponible. Verifiez votre webcam et les permissions.")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)
            self._camera_label.setText("Camera indisponible")

    def _stop_camera(self) -> None:
        """Arrete proprement la webcam."""
        self._camera_timer.stop()
        self._camera_service.stop()
        self._current_frame = None

    def _refresh_camera(self) -> None:
        """Affiche en continu le flux webcam dans le label avec overlay visage."""
        frame = self._camera_service.read_frame()
        if frame is None:
            return

        self._current_frame = frame.copy()
        display = frame.copy()

        # Real-time face detection overlay
        gray = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        faces = self._face_detector.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80)
        )

        if len(faces) == 1:
            x, y, w_f, h_f = faces[0]
            # Green bounding box with rounded corners effect
            cv2.rectangle(display, (x, y), (x + w_f, y + h_f), (54, 134, 35), 2)
            # Corner accents (thicker lines at corners)
            corner_len = 20
            color = (54, 200, 54)  # Bright green
            t = 3
            # Top-left
            cv2.line(display, (x, y), (x + corner_len, y), color, t)
            cv2.line(display, (x, y), (x, y + corner_len), color, t)
            # Top-right
            cv2.line(display, (x + w_f, y), (x + w_f - corner_len, y), color, t)
            cv2.line(display, (x + w_f, y), (x + w_f, y + corner_len), color, t)
            # Bottom-left
            cv2.line(display, (x, y + h_f), (x + corner_len, y + h_f), color, t)
            cv2.line(display, (x, y + h_f), (x, y + h_f - corner_len), color, t)
            # Bottom-right
            cv2.line(display, (x + w_f, y + h_f), (x + w_f - corner_len, y + h_f), color, t)
            cv2.line(display, (x + w_f, y + h_f), (x + w_f, y + h_f - corner_len), color, t)
            # Label
            cv2.putText(display, "Visage detecte", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (54, 200, 54), 2)
        elif len(faces) > 1:
            for (x, y, w_f, h_f) in faces:
                cv2.rectangle(display, (x, y), (x + w_f, y + h_f), (51, 54, 218), 2)
            cv2.putText(display, "Plusieurs visages!", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (51, 54, 218), 2)

        # Pulsing blue border during scan
        if self._is_scanning:
            self._scan_pulse_step = (self._scan_pulse_step + 1) % 30
            alpha = abs(15 - self._scan_pulse_step) / 15.0
            blue_val = int(150 + 105 * alpha)
            self._camera_label.setStyleSheet(
                f"background-color: {Colors.BG_TERTIARY}; "
                f"border: 3px solid rgba(31, 111, 235, {alpha:.2f}); border-radius: 12px;"
            )

        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(
            self._camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self._camera_label.setPixmap(pixmap)

    def _on_scan_clicked(self) -> None:
        """Capture la frame courante puis lance le pipeline d'auth."""
        if self._current_frame is None:
            self._status_label.setText("Impossible de capturer une image. Verifiez la camera.")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)
            return

        self._scan_button.setEnabled(False)
        self._is_scanning = True
        self._scan_pulse_step = 0
        self._status_label.setText("⏳  Analyse biométrique en cours...")
        self._status_label.setStyleSheet(SCAN_STATUS_LOADING)

        self._worker = ScanWorker(self._auth_controller, self._current_frame)
        self._worker.finished.connect(self._on_scan_finished)
        self._worker.start()

    def _on_scan_finished(self, result) -> None:
        """Traite le resultat de scan et declenche la navigation si besoin."""
        self._scan_button.setEnabled(True)
        self._is_scanning = False
        # Reset camera border
        self._camera_label.setStyleSheet(
            f"background-color: {Colors.BG_TERTIARY}; border: 2px solid {Colors.BORDER}; border-radius: 12px;"
        )

        if result.status == AuthStatus.NO_FACE:
            self._status_label.setText("❌  Aucun visage detecte. Placez-vous face a la camera.")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)
            return

        if result.status == AuthStatus.MULTIPLE_FACES:
            self._status_label.setText("⚠️  Plusieurs visages detectes. Une seule personne autorisee.")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)
            return

        if result.status == AuthStatus.CAMERA_ERROR:
            self._status_label.setText(f"❌  {result.message or 'Erreur camera.'}")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)
            return

        if result.status == AuthStatus.ADMIN:
            self._status_label.setText("✅  Administrateur reconnu.")
            self._status_label.setStyleSheet(SCAN_STATUS_SUCCESS)
            self._camera_label.setStyleSheet(
                f"background-color: {Colors.BG_TERTIARY}; border: 2px solid {Colors.ACCENT_GREEN}; border-radius: 12px;"
            )
        elif result.status == AuthStatus.AUTHORIZED:
            self._status_label.setText(f"✅  Authentification reussie : {result.full_name}")
            self._status_label.setStyleSheet(SCAN_STATUS_SUCCESS)
            self._camera_label.setStyleSheet(
                f"background-color: {Colors.BG_TERTIARY}; border: 2px solid {Colors.ACCENT_GREEN}; border-radius: 12px;"
            )
        elif result.status == AuthStatus.UNAUTHORIZED:
            self._status_label.setText("🚫  Utilisateur reconnu mais non autorise.")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)
            self._camera_label.setStyleSheet(
                f"background-color: {Colors.BG_TERTIARY}; border: 2px solid {Colors.ACCENT_RED}; border-radius: 12px;"
            )
        elif result.status == AuthStatus.UNKNOWN:
            self._status_label.setText("❓  Visage inconnu — Redirection vers l'inscription.")
            self._status_label.setStyleSheet(SCAN_STATUS_ERROR)

        QTimer.singleShot(350, lambda: self._auth_controller.apply_navigation(result, self))

    def _set_ready_state(self) -> None:
        """Remet un message utilisateur propre apres un echec."""
        if self._camera_service.is_running:
            self._status_label.setText("Pret pour un nouveau scan.")
            self._status_label.setStyleSheet(SCAN_STATUS_IDLE)
