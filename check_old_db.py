import sqlite3

# Eski veritabanına bağlan
conn = sqlite3.connect('db.sqlite3.backup')
cur = conn.cursor()

# Tabloları listele
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("Eski veritabanındaki tablolar:")
for table in tables:
    print(f"- {table[0]}")

print("\nEski musteri tablosundaki kayıtlar:")
try:
    cur.execute("SELECT first_name, last_name FROM musteri_customer")
    customers = cur.fetchall()
    print(f"Toplam müşteri sayısı: {len(customers)}")
    print("\nİlk 5 müşteri:")
    for customer in customers[:5]:
        print(f"- {customer[0]} {customer[1]}")

    print("\nTablo yapısı:")
    cur.execute("PRAGMA table_info(musteri_customer)")
    columns = cur.fetchall()
    for col in columns:
        print(f"- {col[1]} ({col[2]})")
except Exception as e:
    print(f"Hata: {e}")

# Bağlantıyı kapat
conn.close()
