import os
import smtplib
from email.message import EmailMessage


class EmailAlertService:
    """
    Service d'envoi d'alertes email.

    Si la configuration SMTP est absente, le service reste non bloquant
    et retourne False sans faire planter l'application.
    """

    def __init__(self):
        self._smtp_host = os.getenv("SECURACCESS_SMTP_HOST", "")
        self._smtp_port = int(os.getenv("SECURACCESS_SMTP_PORT", "587"))
        self._smtp_user = os.getenv("SECURACCESS_SMTP_USER", "")
        self._smtp_password = os.getenv("SECURACCESS_SMTP_PASSWORD", "")
        self._from_email = os.getenv("SECURACCESS_ALERT_FROM", self._smtp_user)
        self._to_email = os.getenv("SECURACCESS_ALERT_TO", "")

    @property
    def is_configured(self) -> bool:
        """Indique si l'envoi SMTP est configurable."""
        return bool(self._smtp_host and self._from_email and self._to_email)

    def send_alert(self, subject: str, body: str) -> bool:
        """Envoie un email d'alerte si SMTP est configure."""
        if not self.is_configured:
            return False

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._from_email
        message["To"] = self._to_email
        message.set_content(body)

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port, timeout=10) as smtp:
                smtp.starttls()
                if self._smtp_user and self._smtp_password:
                    smtp.login(self._smtp_user, self._smtp_password)
                smtp.send_message(message)
            return True
        except Exception:
            return False
