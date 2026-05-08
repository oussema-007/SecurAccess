# =============================================================================
# main.py
# Point d'entrée principal de l'application SecurAccess
#
# Rôle de ce fichier :
#   1. Créer l'application PyQt5 et configurer le style global
#   2. Créer la fenêtre principale (QMainWindow)
#   3. Instancier les services (auth, enrollment, log)
#   4. Instancier et enregistrer toutes les pages dans le Router
#   5. Naviguer vers la page de login pour démarrer
#   6. Lancer la boucle d'événements Qt
#
# Pour exécuter :
#   python main.py
#
# Prérequis :
#   pip install PyQt5 opencv-python Pillow
# =============================================================================

import onnxruntime  # FIX: Import onnxruntime first to avoid DLL conflicts with cv2/PyQt5
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# ── Core ──────────────────────────────────────────────────────────────────────
from app.core.router  import Router
from app.core.session import Session
from app.controllers.auth_controller import AuthController

# ── Services ──────────────────────────────────────────────────────────────────
from app.services.auth_service        import AuthService
from app.services.alert_service       import AlertService
from app.services.camera_service      import CameraService
from app.services.database_service    import DatabaseService
from app.services.email_alert_service import EmailAlertService
from app.services.enrollment_service  import EnrollmentService
from app.services.face_detection_service import FaceDetectionService
from app.services.log_service         import LogService
from app.services.upgrade_service     import UpgradeService
from app.services.watermark_service   import WatermarkService

# ── Pages principales ─────────────────────────────────────────────────────────
from app.ui.login_page          import LoginPage
from app.ui.welcome_page        import WelcomePage
from app.ui.access_denied_page  import AccessDeniedPage
from app.ui.unknown_face_page   import UnknownFacePage
from app.ui.enrollment_page     import EnrollmentPage

# ── Dashboard Admin ───────────────────────────────────────────────────────────
from app.ui.admin.admin_dashboard import AdminDashboard

# ── Styles ────────────────────────────────────────────────────────────────────
from app.resources.styles import MAIN_STYLESHEET


# =============================================================================
# Fenêtre principale
# =============================================================================
class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application.
    Contient un QStackedWidget géré par le Router pour la navigation entre pages.
    Toutes les pages sont instanciées une seule fois au démarrage.
    """

    def __init__(self):
        super().__init__()

        # ── Configuration de la fenêtre ────────────────────────────────────
        self.setWindowTitle("SecurAccess — Contrôle d'Accès Biométrique")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        # Centrer la fenêtre sur l'écran
        self._center_window()

        # ── Instanciation des services (injectés dans les pages) ───────────
        self._database_service   = DatabaseService()
        self._watermark_service  = WatermarkService()
        self._log_service        = LogService(self._database_service, self._watermark_service)
        self._alert_service      = AlertService(self._database_service)
        self._email_alert_service = EmailAlertService()
        self._auth_service       = AuthService(self._database_service)
        self._camera_service     = CameraService(camera_index=0)
        self._face_detector      = FaceDetectionService()
        self._auth_controller    = AuthController(
            face_detection_service=self._face_detector,
            auth_service=self._auth_service,
            log_service=self._log_service,
            alert_service=self._alert_service,
            email_alert_service=self._email_alert_service,
        )
        self._enrollment_service = EnrollmentService()
        self._upgrade_service    = UpgradeService()

        # ── QStackedWidget : conteneur central de toutes les pages ─────────
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # ── Initialisation du Router ───────────────────────────────────────
        router = Router.get_instance()
        router.initialize(self._stack)

        # ── Instanciation et enregistrement des pages ──────────────────────
        self._register_pages(router)

        # ── Démarrage : afficher la page de login ──────────────────────────
        router.navigate("login")

    def _register_pages(self, router: Router) -> None:
        """
        Crée toutes les pages et les enregistre dans le Router.
        L'ordre n'a pas d'importance pour le routeur.
        """

        # Page de connexion (injection du service d'auth)
        login_page = LoginPage(
            camera_service=self._camera_service,
            auth_controller=self._auth_controller,
        )
        router.register_page("login", login_page)

        # Page de bienvenue (utilisateur connecté)
        welcome_page = WelcomePage()
        welcome_page.set_services(self._log_service, self._upgrade_service)
        router.register_page("welcome", welcome_page)

        # Page d'accès refusé
        denied_page = AccessDeniedPage()
        router.register_page("access_denied", denied_page)

        # Page visage inconnu
        unknown_page = UnknownFacePage()
        router.register_page("unknown_face", unknown_page)

        # Formulaire de demande d'inscription
        enrollment_page = EnrollmentPage(enrollment_service=self._enrollment_service)
        router.register_page("enrollment", enrollment_page)

        # Dashboard administrateur (injection des deux services)
        admin_dashboard = AdminDashboard(
            log_service        = self._log_service,
            enrollment_service = self._enrollment_service,
            alert_service      = self._alert_service,
        )
        router.register_page("admin_dashboard", admin_dashboard)

    def _center_window(self) -> None:
        """Centre la fenêtre sur l'écran principal."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width()  - self.width())  // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)


# =============================================================================
# Point d'entrée
# =============================================================================
def main():
    """Lance l'application PyQt5."""

    # Activer le rendu haute résolution sur les écrans HiDPI (4K, Retina)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # ── Police par défaut ──────────────────────────────────────────────────
    font = QFont("Inter", 12)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    # ── Application du thème global ────────────────────────────────────────
    app.setStyleSheet(MAIN_STYLESHEET)

    # ── Métadonnées de l'application ───────────────────────────────────────
    app.setApplicationName("SecurAccess")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SecurAccess Academic Project")

    # ── Création et affichage de la fenêtre ───────────────────────────────
    window = MainWindow()
    window.show()

    # ── Boucle d'événements Qt ────────────────────────────────────────────
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
