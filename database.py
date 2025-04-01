import sqlite3

# Connect to SQLite
conn = sqlite3.connect("billing.db")
cursor = conn.cursor()

# Create table for invoices
cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT UNIQUE,
    date TEXT,
    customer_name TEXT,
    customer_address TEXT,
    items TEXT,
    total_amount REAL
)
""")

conn.commit()
conn.close()

print("Database setup completed successfully!")
