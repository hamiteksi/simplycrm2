from django.db import models
from django.utils import timezone

class Communication(models.Model):
    COMMUNICATION_TYPES = [
        ('PHONE', 'Telefon'),
        ('EMAIL', 'E-posta'),
        ('SMS', 'SMS'),
        ('WHATSAPP', 'WhatsApp'),
        ('MEETING', 'Görüşme'),
        ('OTHER', 'Diğer'),
    ]
    
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='communications')
    type = models.CharField(max_length=20, choices=COMMUNICATION_TYPES)
    description = models.TextField()
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - {self.get_type_display()} - {self.date}"
    
    class Meta:
        verbose_name = "İletişim Kaydı"
        verbose_name_plural = "İletişim Kayıtları"
        ordering = ['-date']

class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    customer_notes = models.TextField(blank=True, null=True)
    
    # Kimlik bilgileri
    identity_number = models.CharField(max_length=20, blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    
    # Pasaport bilgileri
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    issuing_authority = models.CharField(max_length=100, blank=True, null=True)
    passport_date = models.DateField(null=True, blank=True)
    passport_info = models.TextField(blank=True, null=True)
    
    # Başvuru bilgileri
    application_type = models.CharField(max_length=50, blank=True, null=True)
    residence_type = models.CharField(max_length=50, blank=True, null=True)
    residence_permit_start_date = models.DateField(null=True, blank=True)
    residence_permit_end_date = models.DateField(null=True, blank=True)
    service_type = models.CharField(max_length=50, blank=True, null=True)
    ptt_code = models.CharField(max_length=100, blank=True, null=True)
    application_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Ödeme bilgileri
    payment_made = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # İletişim geçmişi
    communication_history = models.ManyToManyField('Communication', blank=True, related_name='related_customers')
    
    # Durum
    STATUS_CHOICES = [
        ('ACTIVE', 'Aktif'),
        ('INACTIVE', 'Pasif'),
        ('PENDING', 'Beklemede'),
        ('COMPLETED', 'Tamamlandı'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    
    # Zaman damgaları
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_status_color(self):
        return {
            'ACTIVE': 'success',
            'INACTIVE': 'danger',
            'PENDING': 'warning',
            'COMPLETED': 'info',
        }.get(self.status, 'secondary')
    
    class Meta:
        verbose_name = "Müşteri"
        verbose_name_plural = "Müşteriler"
        ordering = ['-created_at']

def get_upload_to(instance, filename):
    return f'customer_files/customer_{instance.customer.id}/{filename}'

class CustomerFile(models.Model):
    customer = models.ForeignKey(Customer, related_name='files', on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to=get_upload_to)
    file_description = models.CharField(max_length=255, blank=True)

class Note(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Not"
        verbose_name_plural = "Notlar"
        ordering = ['-created_at']

class Expense(models.Model):
    AGE_CHOICES = [(i, str(i)) for i in range(1, 121)]
    COUNTRY_CHOICES = [('TR', 'Turkey'), ('US', 'USA'), ('UK', 'United Kingdom')]  # Just an example

    age = models.PositiveIntegerField(choices=AGE_CHOICES)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    contract_fee = models.BooleanField(default=False)
    population_fee = models.BooleanField(default=False)
    card_fee = models.BooleanField(default=False)

class ExpenseItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='expenses')
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - {self.amount} TL - {self.date}"
    
    class Meta:
        verbose_name = "Gider"
        verbose_name_plural = "Giderler"
        ordering = ['-date']

class Country(models.Model):
    name = models.CharField(max_length=200)
    fee_first_year = models.DecimalField(max_digits=10, decimal_places=2)
    fee_next_year = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class InsuranceAgeBracket(models.Model):
    age = models.CharField(max_length=200)
    fee_first = models.DecimalField(max_digits=10, decimal_places=2)
    fee_second = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.age


class Yapilacak(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='yapilacaklar')
    baslik = models.CharField(max_length=200)
    aciklama = models.TextField(blank=True, null=True)
    son_tarih = models.DateTimeField()
    tamamlandi = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.baslik} - {self.son_tarih.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Yapılacak"
        verbose_name_plural = "Yapılacaklar"
        ordering = ['son_tarih']

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer} - {self.amount} TL - {self.date.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Ödeme"
        verbose_name_plural = "Ödemeler"
        ordering = ['-date']

class CalendarEvent(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='calendar_events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        verbose_name = "Takvim Etkinliği"
        verbose_name_plural = "Takvim Etkinlikleri"
        ordering = ['start_time']
