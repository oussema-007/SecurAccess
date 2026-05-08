"""
Script d'enrolement photo pour un compte admin.

Usage:
    python scripts/enroll_admin.py --email alice.martin@securaccess.fr --samples 15

Touches:
    SPACE : capturer un echantillon
    Q     : quitter
"""

import argparse
from pathlib import Path
import sys

import cv2

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enroler un admin avec des photos webcam")
    parser.add_argument("--email", required=True, help="Email du compte admin existant")
    parser.add_argument("--samples", type=int, default=15, help="Nombre de captures")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from app.services.database_service import DatabaseService
    from app.services.face_biometric_service import FaceBiometricService

    db = DatabaseService()
    biometric = FaceBiometricService(db)

    user = db.fetch_one(
        """
        SELECT id, full_name, role
        FROM users
        WHERE email = ?
        """,
        (args.email,),
    )
    if not user:
        raise RuntimeError("Compte introuvable pour cet email.")
    if user["role"] != "admin":
        raise RuntimeError("Ce script est reserve a un compte admin.")

    user_id = int(user["id"])
    full_name = user["full_name"]

    output_dir = Path("data/faces/admin")
    output_dir.mkdir(parents=True, exist_ok=True)

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        raise RuntimeError("Impossible d'ouvrir la webcam.")

    print(f"Enrolement admin: {full_name} ({args.email})")
    print(f"Captures attendues: {args.samples}")
    print("SPACE pour capturer, Q pour quitter.")

    captured = 0
    while captured < args.samples:
        ok, frame = camera.read()
        if not ok:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (46, 166, 218), 2)

        cv2.putText(
            frame,
            f"Captures: {captured}/{args.samples}",
            (16, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.imshow("Enrollment Admin", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        if key == ord(" ") and len(faces) == 1:
            x, y, w, h = faces[0]
            face_roi = frame[y : y + h, x : x + w]
            embedding = biometric.build_embedding(face_roi)

            image_path = output_dir / f"admin_{user_id}_{captured + 1:03d}.jpg"
            cv2.imwrite(str(image_path), face_roi)
            biometric.save_template(user_id=user_id, embedding=embedding, image_path=str(image_path))
            captured += 1
            print(f"[OK] Capture {captured}/{args.samples}")
        elif key == ord(" "):
            print("[INFO] Une seule face doit etre detectee pour capturer.")

    camera.release()
    cv2.destroyAllWindows()
    print(f"Enrolement termine: {captured} capture(s) enregistree(s).")


if __name__ == "__main__":
    main()
