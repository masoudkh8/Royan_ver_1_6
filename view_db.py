import sqlite3

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

# لیست جداول
print("📊 جداول موجود:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# نمایش داده‌های هر جدول
print("\n📝 داده‌های جداول:")
for table in tables:
    table_name = table[0]
    if not table_name.startswith('sqlite_'):  # جداول داخلی SQLite را نادیده بگیر
        print(f"\n--- {table_name} ---")
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")  # فقط ۵ ردیف اول
        rows = cursor.fetchall()
        if rows:
            # نام ستون‌ها
            columns = [desc[0] for desc in cursor.description]
            print(" | ".join(columns))
            print("-" * 50)
            for row in rows:
                print(" | ".join(str(x) for x in row))
        else:
            print("  (جدول خالی است)")

conn.close()