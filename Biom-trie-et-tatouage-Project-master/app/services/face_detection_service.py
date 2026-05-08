from typing import Optional

import cv2
import numpy as np

from app.models.face_detection_result import FaceDetectionResult, FaceDetectionStatus


class FaceDetectionService:
    """
    Service de detection de visages.

    Utilise Haar Cascade pour une premiere etape simple et robuste.
    """

    def __init__(self):
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._detector = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, frame: np.ndarray) -> FaceDetectionResult:
        """
        Detecte les visages dans une frame BGR OpenCV.

        Retourne un resultat structure pour distinguer 0, 1 ou plusieurs visages.
        """
        if frame is None:
            return FaceDetectionResult(
                status=FaceDetectionStatus.DETECTOR_ERROR,
                message="Frame invalide pour la detection.",
            )

        if self._detector.empty():
            return FaceDetectionResult(
                status=FaceDetectionStatus.DETECTOR_ERROR,
                message="Le detecteur Haar Cascade n'a pas pu etre initialise.",
            )

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        faces = self._detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=6,
            minSize=(80, 80),
        )

        boxes = [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]
        if len(boxes) == 0:
            return FaceDetectionResult(
                status=FaceDetectionStatus.NO_FACE,
                boxes=[],
                message="Aucun visage detecte. Positionnez-vous face a la camera.",
            )
        if len(boxes) > 1:
            return FaceDetectionResult(
                status=FaceDetectionStatus.MULTIPLE_FACES,
                boxes=boxes,
                message="Plusieurs visages detectes. Une seule personne est autorisee par capture.",
            )

        return FaceDetectionResult(
            status=FaceDetectionStatus.SINGLE_FACE,
            boxes=boxes,
            message="Visage detecte avec succes.",
        )
