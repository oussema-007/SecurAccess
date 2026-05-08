import hashlib
import hmac
import os


class WatermarkService:
    """
    Service de tatouage numerique des logs.

    Le tatouage utilise HMAC-SHA256 sur la charge utile du log.
    """

    def __init__(self, secret_key: str = ""):
        env_key = os.getenv("SECURACCESS_LOG_SECRET", "")
        key = secret_key or env_key or "securaccess-dev-secret-key"
        self._secret = key.encode("utf-8")

    def build_payload_hash(self, payload: str) -> str:
        """Construit un hash SHA256 simple de la charge utile."""
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def sign_payload(self, payload: str) -> str:
        """Signe une charge utile avec HMAC-SHA256."""
        return hmac.new(self._secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verifie qu'une signature correspond a la charge utile."""
        expected = self.sign_payload(payload)
        return hmac.compare_digest(expected, signature)
