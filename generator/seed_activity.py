import os
import random
import time

import psycopg2

PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
PG_PORT = os.environ.get("POSTGRES_PORT", "5432")
PG_DB = os.environ.get("POSTGRES_DB", "ecommerce")
PG_USER = os.environ.get("POSTGRES_USER", "ecommerce")
PG_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "ecommerce")
INTERVAL_SECONDS = float(os.environ.get("INTERVAL_SECONDS", "3"))

FIRST_NAMES = ["Sam", "Lea", "Noah", "Emma", "Liam", "Mia", "Theo", "Zoe"]
LAST_NAMES = ["Petit", "Durand", "Lefevre", "Moreau", "Simon", "Laurent"]
CITIES = ["Lyon", "Nice", "Lille", "Marseille", "Toulouse", "Nantes"]
ORDER_STATUSES = ["pending", "shipped", "delivered", "cancelled"]


def connect():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD
    )


def new_customer(cur):
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = f"{first.lower()}.{last.lower()}{random.randint(1, 9999)}@example.com"
    address = f"{random.randint(1, 200)} Rue des Lilas, {random.choice(CITIES)}"
    cur.execute(
        "INSERT INTO customers (first_name, last_name, email, address) "
        "VALUES (%s, %s, %s, %s) RETURNING customer_id",
        (first, last, email, address),
    )
    customer_id = cur.fetchone()[0]
    print(f"[new_customer] customer_id={customer_id} {first} {last}")


def new_order(cur):
    cur.execute("SELECT customer_id FROM customers ORDER BY random() LIMIT 1")
    row = cur.fetchone()
    if not row:
        return
    customer_id = row[0]
    cur.execute(
        "INSERT INTO orders (customer_id) VALUES (%s) RETURNING order_id", (customer_id,)
    )
    order_id = cur.fetchone()[0]

    cur.execute("SELECT product_id, price FROM products")
    products = cur.fetchall()
    for product_id, price in random.sample(products, k=random.randint(1, 3)):
        quantity = random.randint(1, 4)
        cur.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) "
            "VALUES (%s, %s, %s, %s)",
            (order_id, product_id, quantity, price),
        )
    print(f"[new_order] order_id={order_id} customer_id={customer_id}")


def advance_order_status(cur):
    cur.execute(
        "SELECT order_id, order_status FROM orders "
        "WHERE order_status != 'delivered' AND order_status != 'cancelled' "
        "ORDER BY random() LIMIT 1"
    )
    row = cur.fetchone()
    if not row:
        return
    order_id, status = row
    next_status = {"pending": "shipped", "shipped": "delivered"}.get(status)
    if not next_status:
        return
    cur.execute(
        "UPDATE orders SET order_status = %s, updated_at = now() WHERE order_id = %s",
        (next_status, order_id),
    )
    print(f"[update_order] order_id={order_id} {status} -> {next_status}")


def update_customer_address(cur):
    cur.execute("SELECT customer_id FROM customers ORDER BY random() LIMIT 1")
    row = cur.fetchone()
    if not row:
        return
    customer_id = row[0]
    new_address = f"{random.randint(1, 200)} Avenue des Tilleuls, {random.choice(CITIES)}"
    cur.execute(
        "UPDATE customers SET address = %s, updated_at = now() WHERE customer_id = %s",
        (new_address, customer_id),
    )
    print(f"[update_customer] customer_id={customer_id} new address")


def cancel_order(cur):
    cur.execute(
        "SELECT order_id FROM orders WHERE order_status = 'pending' "
        "ORDER BY random() LIMIT 1"
    )
    row = cur.fetchone()
    if not row:
        return
    order_id = row[0]
    cur.execute(
        "UPDATE orders SET order_status = 'cancelled', updated_at = now() "
        "WHERE order_id = %s",
        (order_id,),
    )
    print(f"[cancel_order] order_id={order_id}")


ACTIONS = [
    (new_customer, 0.15),
    (new_order, 0.45),
    (advance_order_status, 0.25),
    (update_customer_address, 0.05),
    (cancel_order, 0.10),
]


def main():
    conn = connect()
    conn.autocommit = True
    print("Seeder started, generating ongoing CDC activity...")
    while True:
        action = random.choices(
            [a for a, _ in ACTIONS], weights=[w for _, w in ACTIONS], k=1
        )[0]
        try:
            with conn.cursor() as cur:
                action(cur)
        except Exception as e:
            print(f"[error] {action.__name__}: {e}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
