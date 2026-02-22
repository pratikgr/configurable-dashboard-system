import sqlite3
conn = sqlite3.connect('dashboard.db')
cursor = conn.cursor()

# Check orders table structure
cursor.execute("PRAGMA table_info(orders)")
print("Orders columns:")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

# Check if orders have 'status' column and what values exist
cursor.execute("SELECT COUNT(*) FROM orders")
print(f"\nTotal orders: {cursor.fetchone()[0]}")

try:
    cursor.execute("SELECT DISTINCT status FROM orders")
    print("Status values:", [r[0] for r in cursor.fetchall()])
except:
    print("No 'status' column exists!")

# Check date range
cursor.execute("SELECT MIN(order_date), MAX(order_date), COUNT(*) FROM orders")
print("Date range:", cursor.fetchone())

# Check if 'amount' column exists
try:
    cursor.execute("SELECT SUM(amount) FROM orders LIMIT 1")
    print("Amount column exists")
except:
    print("No 'amount' column - check order_items instead")

conn.close()
exit()