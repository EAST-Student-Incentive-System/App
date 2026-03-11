import sqlite3
conn = sqlite3.connect('temp-database.db')
cursor = conn.cursor()
print(cursor.execute('PRAGMA table_info(attendance);').fetchall())
conn.close()
