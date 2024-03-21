from django.contrib import admin
from django.db import models

from .models import Customer, Expense, Country, InsuranceAgeBracket, ExpenseItem, Yapilacak

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name')  # Gösterilecek alanlar
    ordering = ('-id',)  # ID'ye göre artan sıralama

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Expense)
admin.site.register(ExpenseItem)
admin.site.register(Country)
admin.site.register(InsuranceAgeBracket)
admin.site.register(Yapilacak)




# Register your models here.
