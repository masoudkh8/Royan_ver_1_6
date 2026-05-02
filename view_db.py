import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# List of tables
print("📊 Existing tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Show داده‌های هر جدول
print("\n📝 Table data:")
for table in tables:
    table_name = table[0]
    if not table_name.startswith('sqlite_'):  # جدfirst Insideی SQLite را نادیده بگیر
        print(f"\n--- {table_name} ---")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")  # فقط 5 Rejectیف first
        rows = cursor.fetchall()
        if rows:
            # Column names
            columns = [desc[0] for desc in cursor.description]
            print(" | ".join(columns))
            print("-" * 50)
            for row in rows:
                print(" | ".join(str(x) for x in row))
        else:
            print("  (Table is empty)")

conn.close()