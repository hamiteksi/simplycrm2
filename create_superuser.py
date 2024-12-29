from django.contrib.auth.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simplycrm.settings')
django.setup()

# Superuser oluştur
username = 'admin'
email = 'admin@example.com'
password = 'admin123'

try:
    superuser = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
    )
    print(f"Superuser başarıyla oluşturuldu: {username}")
except Exception as e:
    print(f"Hata: {e}")
