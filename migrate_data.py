import sqlite3
import json
from datetime import datetime

# Bağlantıları oluştur
old_conn = sqlite3.connect('db.sqlite3.backup')
new_conn = sqlite3.connect('db.sqlite3')

old_cur = old_conn.cursor()
new_cur = new_conn.cursor()

# Müşteri verilerini al
old_cur.execute('SELECT * FROM musteri_customer')
customers = old_cur.fetchall()

# Sütun isimlerini al
old_cur.execute('PRAGMA table_info(musteri_customer)')
columns = old_cur.fetchall()
column_names = [column[1] for column in columns]

# Yeni tabloya ekle
for customer in customers:
    # Yeni tablodaki sütunlar için bir sözlük oluştur
    customer_data = dict(zip(column_names, customer))
    
    # Yeni tabloya eklenecek alanları belirle
    fields = [
        'first_name', 'last_name', 'email', 'phone', 'address', 'customer_notes',
        'identity_number', 'nationality', 'date_of_birth', 'marital_status',
        'passport_number', 'issuing_authority', 'passport_date', 'passport_info',
        'application_type', 'residence_type', 'residence_permit_start_date',
        'residence_permit_end_date', 'service_type', 'ptt_code',
        'application_number', 'payment_made', 'status', 'created_at', 'updated_at'
    ]
    
    # Eski verilerden yeni tabloya uygun veri seti oluştur
    values = []
    placeholders = []
    
    for field in fields:
        if field == 'email':
            values.append(customer_data.get('mail'))
        elif field == 'phone':
            values.append(customer_data.get('phone_number'))
        elif field == 'customer_notes':
            values.append(None)  # Yeni alan
        elif field == 'created_at':
            values.append(datetime.now().isoformat())
        elif field == 'updated_at':
            values.append(datetime.now().isoformat())
        else:
            values.append(customer_data.get(field))
        placeholders.append('?')
    
    # SQL sorgusunu oluştur
    sql = f'''INSERT INTO musteri_customer 
             ({', '.join(fields)}) 
             VALUES ({', '.join(placeholders)})'''
    
    # Verileri ekle
    try:
        new_cur.execute(sql, values)
        new_conn.commit()
    except Exception as e:
        print(f"Hata: {e}")
        print(f"SQL: {sql}")
        print(f"Values: {values}")

# Bağlantıları kapat
old_conn.close()
new_conn.close()

print("Veri aktarımı tamamlandı!")
