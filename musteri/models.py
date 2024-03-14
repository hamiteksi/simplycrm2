from django.db import models
from django.utils import timezone

class Communication(models.Model):
    date = models.DateTimeField()
    method = models.CharField(max_length=100)
    details = models.TextField()

class Customer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    identity_number = models.CharField(max_length=11, null=True, blank=True)  # Kimlik numarası genellikle 11 hanelidir
    nationality = models.CharField(max_length=30, null=True, blank=True)  
    date_of_birth = models.DateField(null=True, blank=True)  
    marital_status = models.CharField(max_length=30, null=True, blank=True)  
    passport_number = models.CharField(max_length=30, null=True, blank=True)
    issuing_authority = models.CharField(max_length=100, null=True)  
    passport_date = models.CharField(max_length=100, null=True, blank=True)  
    application_type = models.CharField(max_length=30, null=True, blank=True)  
    residence_type = models.CharField(max_length=30, null=True, blank=True) 
    residence_permit_start_date  = models.DateField(null=True, blank=True)
    residence_permit_end_date  = models.DateField(null=True, blank=True)
    passport_info = models.CharField(max_length=100, null=True, blank=True)
    service_type = models.CharField(max_length=100, blank=True)
    ptt_code = models.CharField(max_length=50, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    payment_made = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    communication_history = models.ManyToManyField(Communication, blank=True)
    application_number = models.CharField(max_length=50, null=True, blank=True)
    mail = models.CharField(max_length=50, null=True, blank=True)

def get_upload_to(instance, filename):
    return f'customer_files/customer_{instance.customer.id}/{filename}'

class CustomerFile(models.Model):
    customer = models.ForeignKey(Customer, related_name='files', on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to=get_upload_to)
    file_description = models.CharField(max_length=255, blank=True)

class Expense(models.Model):
    AGE_CHOICES = [(i, str(i)) for i in range(1, 121)]
    COUNTRY_CHOICES = [('TR', 'Turkey'), ('US', 'USA'), ('UK', 'United Kingdom')]  # Just an example

    age = models.PositiveIntegerField(choices=AGE_CHOICES)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    contract_fee = models.BooleanField(default=False)
    population_fee = models.BooleanField(default=False)
    card_fee = models.BooleanField(default=False)

class ExpenseItem(models.Model):
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name
    
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
    yapilacak = models.CharField(max_length=255)
    detay = models.TextField(null=True, blank=True)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    tamamlandi = models.BooleanField(default=False)
    tamamlanma_tarihi = models.DateTimeField(null=True, blank=True)  # New field

    def __str__(self):
        return self.yapilacak

