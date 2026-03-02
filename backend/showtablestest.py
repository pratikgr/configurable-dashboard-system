import sqlite3

conn = sqlite3.connect('dashboard.db')
c = conn.cursor()
c.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = [t[0] for t in c.fetchall()]

print("Tables in database:")
for table in tables:
    c.execute(f'SELECT COUNT(*) FROM {table}')
    count = c.fetchone()[0]
    print(f"  • {table}: {count} rows")

conn.close()