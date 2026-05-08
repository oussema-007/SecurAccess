import json
from datetime import datetime
from typing import Optional, Tuple

import cv2
import numpy as np

from app.services.database_service import DatabaseService


class FaceBiometricService:
    """
    Service d'enrolement et de matching biometrique base sur ArcFace.

    ArcFace est charge via insightface.model_zoo (mode CPU). Le service
    manipule des embeddings 512D normalises en L2.
    """

    EMBEDDING_SIZE = (112, 112)

    def __init__(self, database_service: DatabaseService):
        self._db = database_service
        self._arcface_model = None
        self._arcface_available = None
        self._arcface_error_message = ""

    def build_embedding(self, face_roi: np.ndarray) -> np.ndarray:
        """
        Construit un embedding ArcFace a partir d'un visage deja croppe.

        Le modele ArcFace attend une image 112x112 en BGR.
        """
        resized = cv2.resize(face_roi, self.EMBEDDING_SIZE).astype(np.uint8)
        model = self._get_arcface_model()

        if model is None:
            # En mode production, on force ArcFace pour eviter les
            # faux positifs lies a un fallback trop simple.
            raise RuntimeError(
                "ArcFace indisponible: impossible de calculer un embedding fiable. "
                f"{self._arcface_error_message}".strip()
            )

        raw_feat = model.get_feat(resized)
        vector = np.array(raw_feat).flatten().astype(np.float32)

        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def save_template(self, user_id: int, embedding: np.ndarray, image_path: str = "") -> int:
        """Sauvegarde un template biometrque en base SQLite."""
        return self._db.execute_returning_id(
            """
            INSERT INTO face_templates(user_id, embedding, image_path, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                int(user_id),
                json.dumps(embedding.tolist()),
                image_path,
                datetime.now().isoformat(),
            ),
        )

    def find_best_user_match(self, embedding: np.ndarray) -> Tuple[Optional[int], float]:
        """
        Compare l'embedding courant avec tous les templates.

        Retourne (user_id, distance) du meilleur match.
        """
        rows = self._db.fetch_all("SELECT user_id, embedding FROM face_templates")
        if not rows:
            return None, float("inf")

        best_user_id = None
        best_distance = float("inf")
        for row in rows:
            stored = np.array(json.loads(row["embedding"]), dtype=np.float32)
            
            # Ignorer si les tailles d'embedding ne correspondent pas
            if stored.shape != embedding.shape:
                continue
                
            # Distance euclidienne (plus faible = plus proche)
            distance = float(np.linalg.norm(embedding - stored))
            if distance < best_distance:
                best_distance = distance
                best_user_id = int(row["user_id"])
        return best_user_id, best_distance

    def _get_arcface_model(self):
        """Charge le modele ArcFace a la demande (lazy loading)."""
        if self._arcface_available is False:
            return None

        if self._arcface_model is None and self._arcface_available is not False:
            try:
                from insightface.model_zoo import get_model
                import os

                # On utilise w600k_r50 (buffalo_l) car le téléchargement d'arcface_r100_v1 échoue souvent
                model_path = os.path.expanduser('~/.insightface/models/buffalo_l/w600k_r50.onnx')
                if not os.path.exists(model_path):
                    from insightface.app import FaceAnalysis
                    # Ceci forcera le téléchargement du pack buffalo_l s'il n'est pas présent
                    FaceAnalysis(name='buffalo_l')

                self._arcface_model = get_model(model_path)
                # ctx_id=-1 force le CPU, compatible sans CUDA.
                self._arcface_model.prepare(ctx_id=-1)
                self._arcface_available = True
            except Exception as exc:
                import traceback
                traceback.print_exc()
                self._arcface_available = False
                self._arcface_model = None
                self._arcface_error_message = f"{type(exc).__name__}: {str(exc)}"
        return self._arcface_model
