import sqlite3

conn = sqlite3.connect('data/securaccess.db')
cur = conn.cursor()

# Tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('Tables:', [r[0] for r in cur.fetchall()])

# Users schema
cur.execute("PRAGMA table_info(users)")
cols = [r[1] for r in cur.fetchall()]
print('Users columns:', cols)

# All users
cur.execute("SELECT * FROM users")
rows = cur.fetchall()
print(f'\nUsers in DB ({len(rows)} total):')
for r in rows:
    print(' ', r)

conn.close()
