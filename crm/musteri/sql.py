from django.db import connection
from django.conf import settings

settings.configure(
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'django',
            'USER': 'root',
            'PASSWORD': 'kahraman',
            'HOST': 'localhost',
            'PORT': '3306',
        }
    },
    # ... more settings here ...
)


def my_custom_sql(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
    return rows

query = """
SELECT mail, COUNT(*) 
FROM musteri_customer 
GROUP BY mail 
HAVING COUNT(*) > 1;
"""

duplicates = my_custom_sql(query)
for mail, count in duplicates:
    print(f"Duplicate: {mail}, Count: {count}")
