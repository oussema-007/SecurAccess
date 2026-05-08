from typing import Optional

import cv2
import numpy as np


class CameraService:
    """
    Service bas niveau de gestion webcam.

    Ce service encapsule OpenCV pour ouvrir, lire et fermer la camera.
    """

    def __init__(self, camera_index: int = 0):
        self._camera_index = camera_index
        self._capture: Optional[cv2.VideoCapture] = None

    def start(self) -> bool:
        """Ouvre la webcam si elle n'est pas deja active."""
        if self.is_running:
            return True

        self._capture = cv2.VideoCapture(self._camera_index, cv2.CAP_DSHOW)
        if not self._capture.isOpened():
            self.stop()
            return False

        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        return True

    def read_frame(self) -> Optional[np.ndarray]:
        """Lit la frame courante en BGR."""
        if not self.is_running:
            return None

        ok, frame = self._capture.read()
        if not ok:
            return None
        return frame

    def stop(self) -> None:
        """Libere proprement la ressource webcam."""
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    @property
    def is_running(self) -> bool:
        """Indique si la webcam est active."""
        return self._capture is not None and self._capture.isOpened()
