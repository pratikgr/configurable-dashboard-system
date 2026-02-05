-- Initialize database schema and sample data for dashboard demo

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create products table
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample customers (50 customers)
INSERT INTO customers (customer_name, email, region) VALUES
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
('Premium Services', 'sales@premiumservices.com', 'Europe')
ON CONFLICT DO NOTHING;

-- Insert sample products (30 products)
INSERT INTO products (product_name, category, unit_price) VALUES
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
('Scanner', 'Electronics', 249.99)
ON CONFLICT DO NOTHING;

-- Generate sample orders (last 90 days)
-- This will create approximately 500 orders with realistic distribution
DO $$
DECLARE
    i INTEGER;
    random_customer_id INTEGER;
    random_date DATE;
    random_amount DECIMAL(10, 2);
BEGIN
    FOR i IN 1..500 LOOP
        -- Random customer
        random_customer_id := (SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 1);
        
        -- Random date in last 90 days
        random_date := CURRENT_DATE - (RANDOM() * 90)::INTEGER;
        
        -- Random amount between 50 and 2000
        random_amount := 50 + (RANDOM() * 1950)::DECIMAL(10, 2);
        
        INSERT INTO orders (customer_id, order_date, amount, status)
        VALUES (
            random_customer_id,
            random_date,
            random_amount,
            CASE WHEN RANDOM() < 0.95 THEN 'completed' ELSE 'pending' END
        );
    END LOOP;
END $$;

-- Generate order items for each order
DO $$
DECLARE
    order_record RECORD;
    items_count INTEGER;
    i INTEGER;
    random_product_id INTEGER;
    random_quantity INTEGER;
    product_price DECIMAL(10, 2);
BEGIN
    FOR order_record IN SELECT order_id FROM orders LOOP
        -- Each order has 1-5 items
        items_count := 1 + (RANDOM() * 4)::INTEGER;
        
        FOR i IN 1..items_count LOOP
            random_product_id := (SELECT product_id FROM products ORDER BY RANDOM() LIMIT 1);
            random_quantity := 1 + (RANDOM() * 5)::INTEGER;
            product_price := (SELECT unit_price FROM products WHERE product_id = random_product_id);
            
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES (
                order_record.order_id,
                random_product_id,
                random_quantity,
                product_price
            );
        END LOOP;
    END LOOP;
END $$;

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
