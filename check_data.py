import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simplycrm.settings')
django.setup()

from musteri.models import Customer

# Tüm müşterileri say
print(f"Toplam müşteri sayısı: {Customer.objects.count()}")

# İlk 5 müşteriyi göster
print("\nİlk 5 müşteri:")
for customer in Customer.objects.all()[:5]:
    print(f"- {customer.first_name} {customer.last_name}")
