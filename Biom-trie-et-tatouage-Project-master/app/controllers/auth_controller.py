from typing import Optional

import numpy as np
from PyQt5.QtWidgets import QMessageBox, QWidget

from app.core.router import Router
from app.core.session import Session
from app.models.auth_result import AuthResult, AuthStatus
from app.models.face_detection_result import FaceDetectionStatus
from app.services.alert_service import AlertService
from app.services.auth_service import AuthService
from app.services.email_alert_service import EmailAlertService
from app.services.face_detection_service import FaceDetectionService
from app.services.log_service import LogService
from app.ui.dialogs.admin_choice_dialog import AdminChoiceDialog


class AuthController:
    """
    Orchestrateur central du flux d'authentification faciale.

    Responsabilites:
    - lancer la detection de visage
    - lancer l'authentification
    - interpreter les statuts
    - router vers la bonne vue
    """

    def __init__(
        self,
        face_detection_service: FaceDetectionService,
        auth_service: AuthService,
        log_service: LogService,
        alert_service: AlertService,
        email_alert_service: EmailAlertService,
    ):
        self._face_detection_service = face_detection_service
        self._auth_service = auth_service
        self._log_service = log_service
        self._alert_service = alert_service
        self._email_alert_service = email_alert_service

    def authenticate_frame(self, frame: np.ndarray) -> AuthResult:
        """Pipeline complet: detection puis authentification."""
        detection = self._face_detection_service.detect_faces(frame)

        if detection.status == FaceDetectionStatus.NO_FACE:
            result = AuthResult(
                status=AuthStatus.NO_FACE,
                message=detection.message,
                authorization_state="NO_FACE",
            )
            self._register_attempt(result)
            return result

        if detection.status == FaceDetectionStatus.MULTIPLE_FACES:
            result = AuthResult(
                status=AuthStatus.MULTIPLE_FACES,
                message=detection.message,
                authorization_state="MULTIPLE_FACES",
            )
            self._register_attempt(result)
            return result

        if detection.status == FaceDetectionStatus.DETECTOR_ERROR:
            result = AuthResult(
                status=AuthStatus.CAMERA_ERROR,
                message=detection.message,
                authorization_state="DETECTION_ERROR",
            )
            self._register_attempt(result)
            return result

        x, y, w, h = detection.boxes[0]
        face_roi = frame[y : y + h, x : x + w]
        result = self._auth_service.authenticate(face_roi)
        self._register_attempt(result)
        return result

    def apply_navigation(self, result: AuthResult, parent_widget: QWidget) -> None:
        """Interprete le resultat et navigue vers la vue cible."""
        router = Router.get_instance()
        session = Session.get_instance()

        if result.status == AuthStatus.ADMIN and result.user:
            dialog = AdminChoiceDialog(result.user, parent=parent_widget)
            choice = dialog.exec_()
            if choice == AdminChoiceDialog.CHOICE_DASHBOARD:
                session.login(result.user, admin_mode=True)
                router.navigate("admin_dashboard")
                return
            if choice == AdminChoiceDialog.CHOICE_USER:
                session.login(result.user, admin_mode=False)
                router.navigate("welcome")
                return
            return

        if result.status == AuthStatus.AUTHORIZED and result.user:
            session.login(result.user, admin_mode=False)
            router.navigate("welcome")
            return

        if result.status == AuthStatus.UNAUTHORIZED:
            denied_page = router.get_page("access_denied")
            if denied_page is not None and hasattr(denied_page, "set_reason"):
                denied_page.set_reason(result.message)
            if result.user:
                session.login(result.user, admin_mode=False)
            router.navigate("access_denied")
            return

        if result.status == AuthStatus.UNKNOWN:
            unknown_page = router.get_page("unknown_face")
            if unknown_page is not None and hasattr(unknown_page, "set_message"):
                unknown_page.set_message(result.message)
            router.navigate("unknown_face")
            return

        if result.status == AuthStatus.CAMERA_ERROR:
            QMessageBox.critical(
                parent_widget,
                "Erreur camera",
                result.message or "La camera est indisponible.",
            )

    def _register_attempt(self, result: AuthResult) -> None:
        """Persiste le log d'authentification et declenche les alertes."""
        status_for_log = self._to_log_status(result.status)
        user_name = result.full_name or "Inconnu"
        user_role = result.role.name if result.role else "Inconnu"
        self._log_service.add_log(
            user_name=user_name,
            user_role=user_role,
            status=status_for_log,
            confidence=result.confidence,
            details=result.message,
        )

        if result.status in (AuthStatus.UNAUTHORIZED, AuthStatus.CAMERA_ERROR):
            title = "Incident de securite detecte"
            message = (
                f"Statut: {result.status.value} | Utilisateur: {user_name} | "
                f"Message: {result.message or 'Non fourni'}"
            )
            alert = self._alert_service.create_alert("critical", title, message)
            self._email_alert_service.send_alert(
                subject=f"[SecurAccess] {alert.title}",
                body=alert.message,
            )
        elif result.status in (AuthStatus.UNKNOWN, AuthStatus.MULTIPLE_FACES):
            self._alert_service.create_alert(
                "warning",
                "Tentative d'authentification anormale",
                f"Statut {result.status.value}: {result.message or 'Aucun detail'}",
            )

    @staticmethod
    def _to_log_status(status: AuthStatus) -> str:
        """Convertit les statuts d'auth en statut d'affichage des logs."""
        mapping = {
            AuthStatus.ADMIN: "Admin",
            AuthStatus.AUTHORIZED: "Autorisé",
            AuthStatus.UNAUTHORIZED: "Refusé",
            AuthStatus.UNKNOWN: "Inconnu",
            AuthStatus.NO_FACE: "Inconnu",
            AuthStatus.MULTIPLE_FACES: "Refusé",
            AuthStatus.CAMERA_ERROR: "Refusé",
        }
        return mapping.get(status, "Inconnu")
