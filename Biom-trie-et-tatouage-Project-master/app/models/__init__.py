# =============================================================================
# models/__init__.py
# Export des modèles pour faciliter les imports
# =============================================================================

from app.models.user import User, Role, ROLE_LABELS, ROLE_COLORS, ROLE_HIERARCHY
from app.models.auth_result import AuthResult, AuthStatus
from app.models.face_detection_result import FaceDetectionResult, FaceDetectionStatus
from app.models.enrollment_request import EnrollmentRequest, RequestStatus
from app.models.upgrade_request import UpgradeRequest, UpgradeStatus

__all__ = [
    "User", "Role", "ROLE_LABELS", "ROLE_COLORS", "ROLE_HIERARCHY",
    "AuthResult", "AuthStatus",
    "FaceDetectionResult", "FaceDetectionStatus",
    "EnrollmentRequest", "RequestStatus",
    "UpgradeRequest", "UpgradeStatus",
]
