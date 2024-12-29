import sqlite3
from datetime import datetime

# Bağlantıları oluştur
old_conn = sqlite3.connect('db2.sqlite3')
new_conn = sqlite3.connect('db_new.sqlite3')

old_cur = old_conn.cursor()
new_cur = new_conn.cursor()

# Yeni veritabanında müşteri tablosunu oluştur
new_cur.execute('''
CREATE TABLE IF NOT EXISTS musteri_customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name varchar(100) NOT NULL,
    last_name varchar(100) NOT NULL,
    email varchar(100),
    phone varchar(20),
    address TEXT,
    customer_notes TEXT,
    identity_number varchar(20),
    nationality varchar(100),
    date_of_birth date,
    marital_status varchar(20),
    passport_number varchar(20),
    issuing_authority varchar(100),
    passport_date date,
    passport_info TEXT,
    application_type varchar(50),
    residence_type varchar(50),
    residence_permit_start_date date,
    residence_permit_end_date date,
    service_type varchar(50),
    ptt_code varchar(100),
    application_number varchar(100),
    payment_made decimal(10,2) NOT NULL DEFAULT 0,
    status varchar(20),
    created_at datetime NOT NULL,
    updated_at datetime NOT NULL
)
''')

# Müşteri verilerini al
old_cur.execute('SELECT * FROM musteri_customer')
customers = old_cur.fetchall()

# Sütun isimlerini al
old_cur.execute('PRAGMA table_info(musteri_customer)')
old_columns = old_cur.fetchall()
old_column_names = [column[1] for column in old_columns]

# Yeni tabloya ekle
for customer in customers:
    # Eski verilerden bir sözlük oluştur
    customer_data = dict(zip(old_column_names, customer))
    
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
        value = None
        if field == 'email':
            value = customer_data.get('mail')
        elif field == 'phone':
            value = customer_data.get('phone_number')
        elif field == 'created_at' or field == 'updated_at':
            value = datetime.now().isoformat()
        elif field == 'payment_made':
            value = customer_data.get('payment_made', 0) or 0  # None değeri 0'a dönüştür
        else:
            value = customer_data.get(field)
        
        values.append(value)
        placeholders.append('?')
    
    # SQL sorgusunu oluştur
    sql = f'''INSERT INTO musteri_customer 
             ({', '.join(fields)}) 
             VALUES ({', '.join(placeholders)})'''
    
    # Verileri ekle
    try:
        new_cur.execute(sql, values)
        new_conn.commit()
        print(f"Müşteri eklendi: {customer_data['first_name']} {customer_data['last_name']}")
    except Exception as e:
        print(f"Hata: {e}")
        print(f"Müşteri: {customer_data['first_name']} {customer_data['last_name']}")
        print(f"Values: {values}")

# Bağlantıları kapat
old_conn.close()
new_conn.close()

print("Veri aktarımı tamamlandı!")
