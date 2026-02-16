"""
Initialize SQLite database with sample data
"""
import sqlite3
import asyncio
from pathlib import Path


async def init_database():
    """Initialize SQLite database"""
    db_path = Path("dashboard.db")
    
    # Connect to SQLite
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("🗄️  Initializing SQLite database...")
    
    # Read and execute SQL file
    sql_file = Path(__file__).parent / "init_sqlite.sql"
    
    if not sql_file.exists():
        print(f"❌ SQL file not found: {sql_file}")
        return
    
    with open(sql_file, 'r') as f:
        sql_script = f.read()
    
    # Execute SQL
    try:
        cursor.executescript(sql_script)
        conn.commit()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM customers")
        customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM order_items")
        order_items = cursor.fetchone()[0]
        
        print("✅ Database initialized successfully!")
        print(f"   Customers: {customers}")
        print(f"   Products: {products}")
        print(f"   Orders: {orders}")
        print(f"   Order Items: {order_items}")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(init_database())
