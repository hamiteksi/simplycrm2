import os
import django
import pandas as pd
from datetime import datetime, timedelta

from django.db import models


import sys
sys.path.append(r"C:\Users\Hamit\Documents\projeler\simplycrm\simplycrm")


# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from musteri.models import Customer


def parse_date(date_str):
    if pd.isna(date_str):
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()  # Excel tarih formatı
    except ValueError:
        return None

def import_customers_from_excel(file_path):
    try:
        # Excel dosyasını oku
        df = pd.read_excel(file_path)

        # Veritabanında zaten bulunan başvuru numaralarını al
        existing_applications = set(Customer.objects.values_list('application_number', flat=True))

        for index, row in df.iterrows():
            application_number = row.get('application_number', None)
            if pd.isna(application_number) or application_number in existing_applications:
                continue  # Aynı başvuru numarası varsa atla

            # Eksik alanları doldur
            customer_data = {
                'first_name': row.get('first_name', 'Unknown'),
                'last_name': row.get('last_name', 'Unknown'),
                'email': row.get('email', None),
                'phone': row.get('phone', None),
                'address': row.get('address', None),
                'identity_number': row.get('identity_number', None),
                'nationality': row.get('nationality', 'Unknown'),
                'date_of_birth': parse_date(row.get('date_of_birth')),
                'marital_status': row.get('marital_status', 'Unknown'),
                'passport_number': row.get('passport_number', None),
                'issuing_authority': row.get('issuing_authority', None),
                'passport_date': parse_date(row.get('passport_date')),
                'application_type': row.get('application_type', None),
                'residence_type': row.get('residence_type', None),
                'residence_permit_start_date': parse_date(row.get('residence_permit_start_date')),
                'residence_permit_end_date': parse_date(row.get('residence_permit_end_date')),
                'service_type': row.get('service_type', None),
                'application_number': application_number,
                'payment_made': row.get('payment_made', 0),
            }

            try:
                # Müşteri oluştur
                Customer.objects.create(**customer_data)
                print(f"Müşteri eklendi: {customer_data['first_name']} {customer_data['last_name']}")
            except Exception as e:
                print(f"Satır {index + 2} eklenirken hata oluştu: {str(e)}")

        print("\nVeri aktarımı tamamlandı!")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")





# Kullanım
if __name__ == '__main__':
    file_path = r'C:\Users\Hamit\Documents\projeler\simplycrm\simplycrm\cleaned_filtered_renamed_customers.xlsx'
    import_customers_from_excel(file_path)


from musteri.models import Customer

# Aynı başvuru numaralarına sahip olan kayıtları bul
duplicates = Customer.objects.values('application_number').annotate(count=models.Count('id')).filter(count__gt=1)

# Aynı başvuru numaralarına sahip kayıtları sil
for duplicate in duplicates:
    application_number = duplicate['application_number']
    records = Customer.objects.filter(application_number=application_number).order_by('created_at')
    
    # İlk kaydı koru, geri kalanları sil
    for record in records[1:]:
        record.delete()

print("Tekrarlanan kayıtlar silindi.")