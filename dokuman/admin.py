from django.contrib import admin
from .models import DokumanKategori, DokumanTipi, Dokuman, BasvuruSureci

# Register your models here.

@admin.register(DokumanKategori)
class DokumanKategoriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad', 'aciklama')

@admin.register(DokumanTipi)
class DokumanTipiAdmin(admin.ModelAdmin):
    list_display = ('ad', 'aciklama')
    search_fields = ('ad', 'aciklama')

@admin.register(Dokuman)
class DokumanAdmin(admin.ModelAdmin):
    list_display = ('musteri', 'dokuman_tipi', 'yuklenme_tarihi', 'son_guncelleme')
    list_filter = ('dokuman_tipi', 'yuklenme_tarihi')
    search_fields = ('musteri__first_name', 'musteri__last_name', 'notlar')
    date_hierarchy = 'yuklenme_tarihi'

@admin.register(BasvuruSureci)
class BasvuruSureciAdmin(admin.ModelAdmin):
    list_display = ('musteri', 'basvuru_tipi', 'durum', 'baslangic_tarihi', 'randevu_tarihi')
    list_filter = ('basvuru_tipi', 'durum')
    search_fields = ('musteri__first_name', 'musteri__last_name', 'notlar')
    date_hierarchy = 'baslangic_tarihi'
