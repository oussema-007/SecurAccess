"""
enroll_user.py — Enrol any user (any role) via webcam using PyQt5 window.

Usage:
    python scripts/enroll_user.py --email ousshd007@email.com --samples 5

Keys:
    SPACE : capture a sample
    Q / ESC : quit
"""

import argparse
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enroler n'importe quel utilisateur via webcam")
    parser.add_argument("--email",   required=True,       help="Email du compte existant")
    parser.add_argument("--samples", type=int, default=5, help="Nombre de captures (defaut: 5)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    import onnxruntime  # FIX: Import onnxruntime first to avoid DLL conflicts
    import cv2
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QFrame
    )
    from PyQt5.QtCore import QTimer, Qt
    from PyQt5.QtGui import QImage, QPixmap, QFont, QColor

    # Initialize Qt FIRST — required so onnxruntime DLL loads correctly
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))

    from app.services.database_service import DatabaseService
    from app.services.face_biometric_service import FaceBiometricService

    db        = DatabaseService()
    biometric = FaceBiometricService(db)

    # ── Fetch user ────────────────────────────────────────────────────────
    user = db.fetch_one(
        "SELECT id, full_name, role FROM users WHERE email = ?",
        (args.email,),
    )
    if not user:
        print(f"[ERROR] No account found for email: {args.email}")
        sys.exit(1)

    user_id   = int(user["id"])
    full_name = user["full_name"]
    role      = user["role"]
    target    = args.samples

    print(f"\nEnrolling: {full_name} ({args.email}) — role: {role}")
    print(f"Capturing {target} sample(s). Click 'Capturer' when face is detected.\n")

    output_dir = Path(f"data/faces/{role}")
    output_dir.mkdir(parents=True, exist_ok=True)

    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        print("[ERROR] Cannot open webcam.")
        sys.exit(1)

    # ── PyQt5 UI ──────────────────────────────────────────────────────────

    captured   = [0]
    last_faces = [()]

    win = QWidget()
    win.setWindowTitle(f"SecurAccess — Enrollment: {full_name}")
    win.setFixedSize(720, 560)
    win.setStyleSheet("background-color: #f8fafc;")

    layout = QVBoxLayout(win)
    layout.setContentsMargins(20, 16, 20, 16)
    layout.setSpacing(10)

    # Title
    lbl_title = QLabel(f"Enrollment — {full_name}")
    lbl_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e2a3e;")
    lbl_title.setAlignment(Qt.AlignCenter)

    # Camera feed
    lbl_cam = QLabel()
    lbl_cam.setFixedSize(680, 400)
    lbl_cam.setAlignment(Qt.AlignCenter)
    lbl_cam.setStyleSheet("background:#e2e8f0; border-radius: 12px;")

    # Status bar
    lbl_status = QLabel("Position your face in front of the camera")
    lbl_status.setAlignment(Qt.AlignCenter)
    lbl_status.setStyleSheet("font-size: 14px; color: #5b6e8c;")

    # Progress
    lbl_progress = QLabel(f"Captures: 0 / {target}")
    lbl_progress.setAlignment(Qt.AlignCenter)
    lbl_progress.setStyleSheet("font-size: 18px; font-weight: 700; color: #1e2a3e;")

    # Buttons
    btn_row = QHBoxLayout()
    btn_capture = QPushButton("  Capturer  (SPACE)")
    btn_capture.setFixedHeight(44)
    btn_capture.setStyleSheet("""
        QPushButton {
            background-color: #3b82f6; color: white;
            border: none; border-radius: 10px;
            font-size: 15px; font-weight: 600;
        }
        QPushButton:hover { background-color: #2563eb; }
        QPushButton:disabled { background-color: #93c5fd; }
    """)

    btn_quit = QPushButton("Quitter")
    btn_quit.setFixedHeight(44)
    btn_quit.setStyleSheet("""
        QPushButton {
            background-color: transparent; color: #5b6e8c;
            border: 1px solid #e2e8f0; border-radius: 10px;
            font-size: 14px;
        }
        QPushButton:hover { border-color: #ef4444; color: #ef4444; }
    """)

    btn_row.addWidget(btn_capture)
    btn_row.addWidget(btn_quit)

    layout.addWidget(lbl_title)
    layout.addWidget(lbl_cam, alignment=Qt.AlignCenter)
    layout.addWidget(lbl_status)
    layout.addWidget(lbl_progress)
    layout.addLayout(btn_row)

    def do_capture():
        faces = last_faces[0]
        if len(faces) != 1:
            lbl_status.setText("Make sure exactly ONE face is visible!")
            lbl_status.setStyleSheet("font-size: 14px; color: #ef4444; font-weight: 600;")
            return

        ok, frame = camera.read()
        if not ok:
            return

        x, y, w, h = faces[0]
        face_roi   = frame[y: y + h, x: x + w]
        embedding  = biometric.build_embedding(face_roi)

        n = captured[0] + 1
        image_path = output_dir / f"{role}_{user_id}_{n:03d}.jpg"
        cv2.imwrite(str(image_path), face_roi)
        biometric.save_template(user_id=user_id, embedding=embedding, image_path=str(image_path))

        captured[0] = n
        print(f"  [OK] Capture {n}/{target} saved.")
        lbl_progress.setText(f"Captures: {n} / {target}")
        lbl_status.setText(f"Capture {n}/{target} saved!")
        lbl_status.setStyleSheet("font-size: 14px; color: #22c55e; font-weight: 600;")

        if n >= target:
            btn_capture.setEnabled(False)
            lbl_status.setText(f"Enrollment complete! {full_name} can now log in.")
            lbl_title.setStyleSheet("font-size: 20px; font-weight: 700; color: #22c55e;")
            print(f"\n[DONE] Enrollment complete — {n} templates saved.")
            QTimer.singleShot(2000, win.close)

    def on_frame():
        ok, frame = camera.read()
        if not ok:
            return

        display = frame.copy()
        gray    = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
        faces   = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80))
        last_faces[0] = faces

        color = (46, 200, 80) if len(faces) == 1 else (218, 54, 51)
        for (x, y, w, h) in faces:
            # Corner brackets
            t, c = 3, 20
            cv2.line(display, (x, y), (x+c, y), color, t)
            cv2.line(display, (x, y), (x, y+c), color, t)
            cv2.line(display, (x+w, y), (x+w-c, y), color, t)
            cv2.line(display, (x+w, y), (x+w, y+c), color, t)
            cv2.line(display, (x, y+h), (x+c, y+h), color, t)
            cv2.line(display, (x, y+h), (x, y+h-c), color, t)
            cv2.line(display, (x+w, y+h), (x+w-c, y+h), color, t)
            cv2.line(display, (x+w, y+h), (x+w, y+h-c), color, t)

        rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        h2, w2, ch = rgb.shape
        img = QImage(rgb.data, w2, h2, ch * w2, QImage.Format_RGB888)
        lbl_cam.setPixmap(
            QPixmap.fromImage(img).scaled(lbl_cam.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        if len(faces) == 1 and captured[0] < target:
            lbl_status.setText("Face detected — press SPACE or click Capturer")
            lbl_status.setStyleSheet("font-size: 14px; color: #22c55e;")
        elif len(faces) == 0 and captured[0] < target:
            lbl_status.setText("No face detected — position yourself in front of camera")
            lbl_status.setStyleSheet("font-size: 14px; color: #5b6e8c;")

    # Keyboard shortcut (Space)
    def keyPressEvent(event):
        if event.key() == Qt.Key_Space:
            do_capture()
        elif event.key() in (Qt.Key_Q, Qt.Key_Escape):
            win.close()
    win.keyPressEvent = keyPressEvent

    btn_capture.clicked.connect(do_capture)
    btn_quit.clicked.connect(win.close)

    timer = QTimer()
    timer.timeout.connect(on_frame)
    timer.start(33)  # ~30 fps

    win.show()
    app.exec_()

    camera.release()
    print(f"\nEnrollment ended: {captured[0]}/{target} sample(s) captured.")


if __name__ == "__main__":
    main()
