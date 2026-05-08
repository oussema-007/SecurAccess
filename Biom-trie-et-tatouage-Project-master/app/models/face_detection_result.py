from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Tuple


class FaceDetectionStatus(Enum):
    """Statuts possibles de detection de visage."""

    NO_FACE = "no_face"
    SINGLE_FACE = "single_face"
    MULTIPLE_FACES = "multiple_faces"
    DETECTOR_ERROR = "detector_error"


@dataclass
class FaceDetectionResult:
    """
    Resultat structure de detection.

    Les boites sont exprimees sous la forme (x, y, width, height).
    """

    status: FaceDetectionStatus
    boxes: List[Tuple[int, int, int, int]] = field(default_factory=list)
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
