CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT NOT NULL,
    address       TEXT NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now(),
    updated_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE products (
    product_id    SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    category      TEXT NOT NULL,
    price         NUMERIC(10, 2) NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now(),
    updated_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
    order_status  TEXT NOT NULL DEFAULT 'pending',
    order_date    TIMESTAMP NOT NULL DEFAULT now(),
    updated_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id      INTEGER NOT NULL REFERENCES orders(order_id),
    product_id    INTEGER NOT NULL REFERENCES products(product_id),
    quantity      INTEGER NOT NULL,
    unit_price    NUMERIC(10, 2) NOT NULL
);

-- Debezium needs the full old row on UPDATE/DELETE to produce a complete
-- "before" image, which the default REPLICA IDENTITY (primary key only)
-- doesn't provide.
ALTER TABLE customers REPLICA IDENTITY FULL;
ALTER TABLE products REPLICA IDENTITY FULL;
ALTER TABLE orders REPLICA IDENTITY FULL;
ALTER TABLE order_items REPLICA IDENTITY FULL;

-- Small seed so there's base data before the generator starts producing
-- ongoing CDC activity.
INSERT INTO customers (first_name, last_name, email, address) VALUES
    ('Alice', 'Martin', 'alice.martin@example.com', '12 Rue de Paris, Lyon'),
    ('Ben', 'Dubois', 'ben.dubois@example.com', '5 Avenue Victor Hugo, Nice'),
    ('Chloe', 'Bernard', 'chloe.bernard@example.com', '8 Rue Nationale, Lille');

INSERT INTO products (name, category, price) VALUES
    ('Wireless Mouse', 'Electronics', 19.99),
    ('Mechanical Keyboard', 'Electronics', 89.99),
    ('Desk Lamp', 'Home', 24.50),
    ('Notebook', 'Office', 3.75),
    ('Water Bottle', 'Home', 12.00);
