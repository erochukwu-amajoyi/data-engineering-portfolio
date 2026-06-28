CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_key INTEGER PRIMARY KEY,
    product TEXT NOT NULL,
    category TEXT NOT NULL,
    UNIQUE (product, category)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_sales (
    order_id INTEGER PRIMARY KEY,
    customer_key INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_product(product_key),
    date_key INTEGER NOT NULL REFERENCES dim_date(date_key),
    amount NUMERIC(12, 2) NOT NULL
);
