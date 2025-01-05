import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from musteri.models import Customer
from django.db.models import Count

def clean_duplicates():
    # Mükerrer başvuru numaralarını bul
    duplicates = Customer.objects.values('application_number')\
        .annotate(count=Count('id'))\
        .filter(count__gt=1, application_number__isnull=False)
    
    print("Mükerrer başvuru numaraları:")
    for dup in duplicates:
        app_num = dup['application_number']
        count = dup['count']
        print(f"Başvuru No: {app_num}, Tekrar Sayısı: {count}")
        
        # Bu başvuru numarasına sahip tüm kayıtları al
        customers = Customer.objects.filter(application_number=app_num).order_by('created_at')
        
        # En eski kaydı tut, diğerlerini sil
        first_customer = customers.first()
        if first_customer:
            print(f"Korunan kayıt ID: {first_customer.id}, Oluşturma Tarihi: {first_customer.created_at}")
            # İlk kayıt hariç diğerlerini sil
            customers.exclude(id=first_customer.id).delete()
            print(f"{count-1} adet mükerrer kayıt silindi\n")

if __name__ == '__main__':
    clean_duplicates()