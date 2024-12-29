import sqlite3

# db2.sqlite3'e bağlan
conn = sqlite3.connect('db2.sqlite3')
cur = conn.cursor()

print("Müşteri tablosundaki kayıtlar:")
try:
    cur.execute("SELECT * FROM musteri_customer")
    customers = cur.fetchall()
    print(f"Toplam müşteri sayısı: {len(customers)}")
    
    # Sütun isimlerini al
    cur.execute("PRAGMA table_info(musteri_customer)")
    columns = cur.fetchall()
    column_names = [col[1] for col in columns]
    print("\nSütunlar:", column_names)
    
    print("\nİlk 5 müşteri:")
    for customer in customers[:5]:
        customer_dict = dict(zip(column_names, customer))
        print(f"- {customer_dict['first_name']} {customer_dict['last_name']}")
        
except Exception as e:
    print(f"Hata: {e}")

# Bağlantıyı kapat
conn.close()
