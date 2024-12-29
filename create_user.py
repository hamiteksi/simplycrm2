import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simplycrm.settings")

import django
django.setup()

from django.contrib.auth.models import User

# Kullanıcı varsa sil
User.objects.filter(username='admin').delete()

# Yeni kullanıcı oluştur
user = User.objects.create_user('admin', password='admin123')
user.is_superuser = True
user.is_staff = True
user.save()

print("Admin kullanıcısı başarıyla oluşturuldu!")
