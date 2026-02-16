-- SQLite Database Initialization Script
-- Initialize database schema and sample data for dashboard demo

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    region TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT,
    unit_price REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date DATE NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'completed',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Insert sample customers (20 customers)
INSERT OR IGNORE INTO customers (customer_name, email, region) VALUES
('Acme Corporation', 'sales@acme.com', 'North America'),
('Global Tech Inc', 'info@globaltech.com', 'Europe'),
('Pacific Traders', 'contact@pacific.com', 'Asia'),
('Atlantic Supplies', 'hello@atlantic.com', 'North America'),
('European Industries', 'sales@euindustries.com', 'Europe'),
('Asian Ventures', 'contact@asianventures.com', 'Asia'),
('Northern Goods', 'info@northerngoods.com', 'North America'),
('Southern Exports', 'sales@southernexports.com', 'South America'),
('Eastern Trading', 'contact@easterntrading.com', 'Asia'),
('Western Solutions', 'info@westernsolutions.com', 'North America'),
('Prime Distributors', 'sales@primedist.com', 'Europe'),
('Elite Enterprises', 'contact@eliteent.com', 'Asia'),
('Mega Corp', 'info@megacorp.com', 'North America'),
('Super Traders', 'sales@supertraders.com', 'Europe'),
('Ultra Goods', 'contact@ultragoods.com', 'Asia'),
('Top Suppliers', 'info@topsuppliers.com', 'North America'),
('Best Vendors', 'sales@bestvendors.com', 'Europe'),
('First Choice', 'contact@firstchoice.com', 'Asia'),
('Quality Products', 'info@qualityproducts.com', 'North America'),
('Premium Services', 'sales@premiumservices.com', 'Europe');

-- Insert sample products (30 products)
INSERT OR IGNORE INTO products (product_name, category, unit_price) VALUES
('Widget Pro', 'Electronics', 299.99),
('Gadget Plus', 'Electronics', 499.99),
('Device Max', 'Electronics', 799.99),
('Tool Kit', 'Tools', 149.99),
('Power Drill', 'Tools', 199.99),
('Saw Set', 'Tools', 249.99),
('Office Chair', 'Furniture', 399.99),
('Desk Lamp', 'Furniture', 79.99),
('File Cabinet', 'Furniture', 299.99),
('Notebook Set', 'Stationery', 29.99),
('Pen Collection', 'Stationery', 19.99),
('Paper Ream', 'Stationery', 39.99),
('Coffee Maker', 'Appliances', 149.99),
('Microwave', 'Appliances', 199.99),
('Blender', 'Appliances', 89.99),
('Laptop Stand', 'Accessories', 49.99),
('Mouse Pad', 'Accessories', 14.99),
('Keyboard', 'Accessories', 79.99),
('Monitor', 'Electronics', 349.99),
('Webcam', 'Electronics', 99.99),
('Headphones', 'Electronics', 149.99),
('Backpack', 'Bags', 59.99),
('Briefcase', 'Bags', 129.99),
('Messenger Bag', 'Bags', 79.99),
('Water Bottle', 'Accessories', 24.99),
('Travel Mug', 'Accessories', 19.99),
('Desk Organizer', 'Accessories', 34.99),
('Whiteboard', 'Office', 89.99),
('Projector', 'Electronics', 599.99),
('Scanner', 'Electronics', 249.99);

-- Generate sample orders (500 orders over last 90 days)
-- Using SQLite's date functions
INSERT INTO orders (customer_id, order_date, amount, status)
WITH RECURSIVE dates(n) AS (
  VALUES(0)
  UNION ALL
  SELECT n+1 FROM dates WHERE n < 499
)
SELECT 
  (ABS(RANDOM()) % 20) + 1 as customer_id,
  DATE('now', '-' || (ABS(RANDOM()) % 90) || ' days') as order_date,
  ROUND(50 + (ABS(RANDOM()) % 1950) + (RANDOM() / 9223372036854775808.0), 2) as amount,
  CASE WHEN (ABS(RANDOM()) % 100) < 95 THEN 'completed' ELSE 'pending' END as status
FROM dates;

-- Generate order items (1-5 items per order)
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
SELECT 
  o.order_id,
  (ABS(RANDOM()) % 30) + 1 as product_id,
  (ABS(RANDOM()) % 5) + 1 as quantity,
  p.unit_price
FROM orders o
CROSS JOIN (SELECT 1 as n UNION SELECT 2 UNION SELECT 3) items
JOIN products p ON p.product_id = (ABS(RANDOM()) % 30) + 1
WHERE (ABS(RANDOM()) % 3) = 0  -- Randomly include items
LIMIT (SELECT COUNT(*) FROM orders) * 2;  -- Average 2 items per order

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- Display summary
SELECT 
    'Database initialized successfully!' as message,
    (SELECT COUNT(*) FROM customers) as customers,
    (SELECT COUNT(*) FROM products) as products,
    (SELECT COUNT(*) FROM orders) as orders,
    (SELECT COUNT(*) FROM order_items) as order_items;
