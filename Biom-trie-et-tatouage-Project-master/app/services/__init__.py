# =============================================================================
# services/__init__.py
# =============================================================================

from app.services.alert_service import AlertService, SecurityAlert
from app.services.auth_service import AuthService
from app.services.camera_service import CameraService
from app.services.database_service import DatabaseService
from app.services.email_alert_service import EmailAlertService
from app.services.enrollment_service import EnrollmentService
from app.services.face_biometric_service import FaceBiometricService
from app.services.face_detection_service import FaceDetectionService
from app.services.log_service import LogService, LogEntry
from app.services.upgrade_service import UpgradeService
from app.services.watermark_service import WatermarkService

__all__ = [
    "AuthService",
    "AlertService",
    "SecurityAlert",
    "CameraService",
    "DatabaseService",
    "EmailAlertService",
    "FaceDetectionService",
    "FaceBiometricService",
    "EnrollmentService",
    "LogService",
    "LogEntry",
    "UpgradeService",
    "WatermarkService",
]
