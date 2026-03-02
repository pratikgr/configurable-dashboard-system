-- Customer Analytics Mock Data
-- Add to existing database or run separately

-- Add more detailed customer data
INSERT INTO customers (customer_id, customer_name, email, region, created_at) VALUES
(51, 'Tech Solutions Inc', 'tech@solutions.com', 'West', '2024-05-15'),
(52, 'Global Traders LLC', 'info@globaltraders.com', 'East', '2024-06-20'),
(53, 'Prime Retailers', 'contact@primeretail.com', 'South', '2024-07-10'),
(54, 'Digital Innovations', 'hello@digitalinnov.com', 'North', '2024-08-05'),
(55, 'Enterprise Corp', 'support@enterprise.com', 'Central', '2024-09-01');

-- Add customer interactions table (new)
CREATE TABLE IF NOT EXISTS customer_interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    interaction_type TEXT, -- 'email', 'call', 'meeting', 'support'
    interaction_date DATE,
    duration_minutes INTEGER,
    outcome TEXT, -- 'positive', 'neutral', 'negative'
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Add sample interactions
INSERT INTO customer_interactions (customer_id, interaction_type, interaction_date, duration_minutes, outcome, notes) VALUES
(1, 'email', '2026-01-15', 0, 'positive', 'Follow-up on order'),
(1, 'call', '2026-01-20', 15, 'positive', 'Product inquiry'),
(2, 'meeting', '2026-01-22', 60, 'positive', 'Quarterly review'),
(3, 'support', '2026-01-25', 30, 'neutral', 'Technical issue'),
(4, 'email', '2026-02-01', 0, 'positive', 'New product interest'),
(5, 'call', '2026-02-05', 20, 'negative', 'Pricing complaint'),
(1, 'meeting', '2026-02-10', 45, 'positive', 'Upsell discussion'),
(2, 'support', '2026-02-12', 25, 'neutral', 'Account setup'),
(3, 'email', '2026-02-15', 0, 'positive', 'Invoice inquiry'),
(4, 'call', '2026-02-18', 10, 'positive', 'Quick question');

-- Add customer satisfaction scores (new table)
CREATE TABLE IF NOT EXISTS customer_satisfaction (
    satisfaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    survey_date DATE,
    nps_score INTEGER, -- Net Promoter Score (0-10)
    satisfaction_score INTEGER, -- 1-5
    feedback TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Add satisfaction data
INSERT INTO customer_satisfaction (customer_id, survey_date, nps_score, satisfaction_score, feedback) VALUES
(1, '2026-01-30', 9, 5, 'Excellent service!'),
(2, '2026-01-30', 8, 4, 'Very satisfied'),
(3, '2026-02-05', 7, 4, 'Good overall'),
(4, '2026-02-05', 6, 3, 'Average experience'),
(5, '2026-02-10', 5, 3, 'Could be better'),
(1, '2026-02-15', 10, 5, 'Outstanding!'),
(2, '2026-02-15', 8, 4, 'Great support'),
(3, '2026-02-20', 9, 5, 'Very happy');
