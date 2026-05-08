"""
enroll_user.py — Launch enrollment as part of the main app (same process).
This avoids the onnxruntime DLL issue by running under main.py's environment.

Usage — run from project root:
    .\.venv\Scripts\python.exe enroll_user.py ousshd007@email.com 5
"""
import onnxruntime  # MUST be first import to avoid DLL conflicts (same as main.py)
import sys

if len(sys.argv) < 2:
    print("Usage: python enroll_user.py <email> [samples]")
    print("Example: python enroll_user.py ousshd007@email.com 5")
    sys.exit(1)

TARGET_EMAIL   = sys.argv[1]
TARGET_SAMPLES = int(sys.argv[2]) if len(sys.argv) > 2 else 5

# ── Bootstrap (same as main.py) ───────────────────────────────────────────────
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QImage, QPixmap, QColor
import cv2

app = QApplication(sys.argv)
app.setFont(QFont("Segoe UI", 11))

# ── Now import services (onnxruntime loads fine after Qt) ─────────────────────
from app.services.database_service import DatabaseService
from app.services.face_biometric_service import FaceBiometricService
from pathlib import Path

db        = DatabaseService()
biometric = FaceBiometricService(db)

# ── Find user ─────────────────────────────────────────────────────────────────
user = db.fetch_one(
    "SELECT id, full_name, role FROM users WHERE email = ?",
    (TARGET_EMAIL,),
)
if not user:
    print(f"[ERROR] No user found with email: {TARGET_EMAIL}")
    print("        Run: .venv\\Scripts\\python.exe scripts\\add_user.py first")
    sys.exit(1)

user_id   = int(user["id"])
full_name = user["full_name"]
role      = user["role"]
print(f"\nEnrolling: {full_name}  |  role: {role}  |  target: {TARGET_SAMPLES} samples\n")

output_dir = Path(f"data/faces/{role}")
output_dir.mkdir(parents=True, exist_ok=True)

detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not camera.isOpened():
    print("[ERROR] Cannot open webcam.")
    sys.exit(1)

# ── Build UI ──────────────────────────────────────────────────────────────────
captured   = [0]
last_faces = [()]

win = QWidget()
win.setWindowTitle(f"SecurAccess Enrollment — {full_name}")
win.setFixedSize(720, 540)
win.setStyleSheet("background-color: #f8fafc;")

layout = QVBoxLayout(win)
layout.setContentsMargins(24, 18, 24, 18)
layout.setSpacing(10)

lbl_title = QLabel(f"Enrollment — {full_name}  ({role.upper()})")
lbl_title.setAlignment(Qt.AlignCenter)
lbl_title.setStyleSheet("font-size: 19px; font-weight: 700; color: #1e2a3e; background: transparent;")

lbl_cam = QLabel()
lbl_cam.setFixedSize(672, 378)
lbl_cam.setAlignment(Qt.AlignCenter)
lbl_cam.setStyleSheet("background:#e2e8f0; border-radius: 12px; border: 2px solid #e2e8f0;")

lbl_status = QLabel("Position your face in front of the camera")
lbl_status.setAlignment(Qt.AlignCenter)
lbl_status.setStyleSheet("font-size: 14px; color: #5b6e8c; background: transparent;")

lbl_progress = QLabel(f"Captures: 0 / {TARGET_SAMPLES}")
lbl_progress.setAlignment(Qt.AlignCenter)
lbl_progress.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e2a3e; background: transparent;")

btn_row = QHBoxLayout()
btn_capture = QPushButton("  Capturer  [SPACE]")
btn_capture.setFixedHeight(46)
btn_capture.setCursor(Qt.PointingHandCursor)
btn_capture.setStyleSheet("""
    QPushButton {
        background-color: #3b82f6; color: white;
        border: none; border-radius: 10px;
        font-size: 15px; font-weight: 600;
    }
    QPushButton:hover { background-color: #2563eb; }
    QPushButton:disabled { background-color: #93c5fd; }
""")

btn_quit = QPushButton("Quitter  [ESC]")
btn_quit.setFixedHeight(46)
btn_quit.setCursor(Qt.PointingHandCursor)
btn_quit.setStyleSheet("""
    QPushButton {
        background-color: transparent; color: #5b6e8c;
        border: 1px solid #e2e8f0; border-radius: 10px;
        font-size: 14px;
    }
    QPushButton:hover { border-color: #ef4444; color: #ef4444; background: #fef2f2; }
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
        lbl_status.setText("Exactly ONE face must be visible!")
        lbl_status.setStyleSheet("font-size: 14px; color: #ef4444; font-weight: 600; background: transparent;")
        return

    ok, frame = camera.read()
    if not ok:
        return

    x, y, w, h = faces[0]
    face_roi   = frame[y: y + h, x: x + w]
    embedding  = biometric.build_embedding(face_roi)
    if embedding is None:
        lbl_status.setText("Could not generate embedding — try again.")
        lbl_status.setStyleSheet("font-size: 14px; color: #ef4444; background: transparent;")
        return

    n = captured[0] + 1
    image_path = output_dir / f"{role}_{user_id}_{n:03d}.jpg"
    cv2.imwrite(str(image_path), face_roi)
    biometric.save_template(user_id=user_id, embedding=embedding, image_path=str(image_path))

    captured[0] = n
    print(f"  [OK] Capture {n}/{TARGET_SAMPLES}")
    lbl_progress.setText(f"Captures: {n} / {TARGET_SAMPLES}")
    lbl_status.setText(f"Saved capture {n}/{TARGET_SAMPLES}!")
    lbl_status.setStyleSheet("font-size: 14px; color: #22c55e; font-weight: 600; background: transparent;")

    if n >= TARGET_SAMPLES:
        btn_capture.setEnabled(False)
        lbl_status.setText(f"Enrollment complete! {full_name} can now log in.")
        lbl_title.setStyleSheet("font-size: 19px; font-weight: 700; color: #22c55e; background: transparent;")
        lbl_cam.setStyleSheet("background:#e2e8f0; border-radius: 12px; border: 2px solid #22c55e;")
        print(f"\n[DONE] {full_name} enrolled with {n} template(s). They can now log in!\n")
        QTimer.singleShot(2500, win.close)


def on_frame():
    ok, frame = camera.read()
    if not ok:
        return

    display = frame.copy()
    gray    = cv2.cvtColor(display, cv2.COLOR_BGR2GRAY)
    faces   = detector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80))
    last_faces[0] = faces

    green = (46, 200, 80)
    red   = (50, 50, 218)
    color = green if len(faces) == 1 else red

    for (x, y, w, h) in faces:
        c, t = 22, 3
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

    if captured[0] < TARGET_SAMPLES:
        if len(faces) == 1:
            lbl_status.setText("Face detected — press SPACE or click Capturer")
            lbl_status.setStyleSheet("font-size: 14px; color: #22c55e; background: transparent;")
        elif len(faces) == 0:
            lbl_status.setText("No face detected — position yourself closer")
            lbl_status.setStyleSheet("font-size: 14px; color: #5b6e8c; background: transparent;")
        else:
            lbl_status.setText("Multiple faces — only one person allowed!")
            lbl_status.setStyleSheet("font-size: 14px; color: #ef4444; background: transparent;")


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
timer.start(33)

win.show()
app.exec_()

camera.release()
print(f"Session ended: {captured[0]}/{TARGET_SAMPLES} sample(s) captured.")
