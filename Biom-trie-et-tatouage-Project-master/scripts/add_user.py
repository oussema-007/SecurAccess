"""
add_user.py — Add a new user account to the SecurAccess database.
The user can then be enrolled with: scripts\enroll_admin.py --email <email>
"""
import sqlite3
import sys
import uuid

# ── User details to add ────────────────────────────────────────────────────
FULL_NAME = "amir"          # Change this to the real name
EMAIL     = "amir@gmail.com"
ROLE      = "user"             # Options: user / pro / ultimate / admin
IS_ACTIVE = 1

# Auto-generate a unique face_id
FACE_ID = f"face_{uuid.uuid4().hex[:10]}"

# ── Insert ─────────────────────────────────────────────────────────────────
conn = sqlite3.connect("data/securaccess.db")
cur  = conn.cursor()

# Check if email already exists
cur.execute("SELECT id FROM users WHERE email = ?", (EMAIL,))
if cur.fetchone():
    print(f"[!] User with email '{EMAIL}' already exists.")
    conn.close()
    sys.exit(0)

cur.execute(
    "INSERT INTO users (face_id, full_name, email, role, is_active) VALUES (?,?,?,?,?)",
    (FACE_ID, FULL_NAME, EMAIL, ROLE, IS_ACTIVE)
)
conn.commit()
new_id = cur.lastrowid
conn.close()

print(f"[OK] User created successfully!")
print(f"     ID       : {new_id}")
print(f"     Name     : {FULL_NAME}")
print(f"     Email    : {EMAIL}")
print(f"     Role     : {ROLE}")
print(f"     Face ID  : {FACE_ID}")
print()
print(f"[NEXT] Now enroll their face by running:")
print(f"       .\.venv\Scripts\python.exe scripts\enroll_admin.py --email {EMAIL}")
