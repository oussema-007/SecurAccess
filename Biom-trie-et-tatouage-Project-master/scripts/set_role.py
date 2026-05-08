import sqlite3, sys
conn = sqlite3.connect('data/securaccess.db')
conn.execute(f"UPDATE users SET role='{sys.argv[2]}' WHERE email='{sys.argv[1]}'")
conn.commit()
conn.close()
print(f'Role updated successfully for {sys.argv[1]}')
