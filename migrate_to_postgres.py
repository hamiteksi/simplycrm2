import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django.setup()

from django.contrib.auth.models import User
from musteri.models import Customer
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

def export_data():
    # Kullanıcıları dışa aktar
    users = User.objects.all()
    users_data = serialize('json', users)
    
    # Müşterileri dışa aktar
    customers = Customer.objects.all()
    customers_data = serialize('json', customers)
    
    # Verileri JSON dosyalarına kaydet
    with open('users_data.json', 'w', encoding='utf-8') as f:
        f.write(users_data)
    
    with open('customers_data.json', 'w', encoding='utf-8') as f:
        f.write(customers_data)
    
    print("Veriler başarıyla dışa aktarıldı!")

if __name__ == '__main__':
    export_data() 