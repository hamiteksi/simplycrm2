from django.db import models
from django.contrib.auth.models import User
from musteri.models import Customer

# Doküman yönetimi için gerekli modelleri ekliyorum

class DokumanKategori(models.Model):
    KATEGORI_TIPLERI = [
        ('VATANDASLIK', 'Vatandaşlık'),
        ('OTURMA_IZNI', 'Oturma İzni'),
        ('GENEL', 'Genel'),
    ]
    
    ad = models.CharField(max_length=50, choices=KATEGORI_TIPLERI)
    aciklama = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.get_ad_display()
    
    class Meta:
        verbose_name = "Doküman Kategorisi"
        verbose_name_plural = "Doküman Kategorileri"

class DokumanTipi(models.Model):
    VATANDASLIK_EVRAKLARI = [
        ('PASAPORT', 'Pasaport'),
        ('DOGUM_BELGESI', 'Doğum Belgesi'),
        ('EVLILIK_BELGESI', 'Evlilik Belgesi'),
        ('ADLI_SICIL', 'Adli Sicil Belgesi'),
        ('SAGLIK_SIGORTASI', 'Sağlık Sigortası'),
        ('BANKA_HESAP', 'Banka Hesap Dökümleri'),
        ('TAPU', 'Tapu Belgesi'),
        ('VERGI_NO', 'Vergi Numarası Belgesi'),
        ('IKAMET_BELGESI', 'İkamet Belgesi'),
        ('FOTOGRAF', 'Biyometrik Fotoğraf'),
    ]
    
    OTURMA_IZNI_EVRAKLARI = [
        ('PASAPORT', 'Pasaport'),
        ('FOTOGRAF', 'Biyometrik Fotoğraf'),
        ('SAGLIK_SIGORTASI', 'Sağlık Sigortası'),
        ('GELIR_BELGESI', 'Gelir Belgesi'),
        ('KIRA_KONTRATI', 'Kira Kontratı'),
        ('OGRENCI_BELGESI', 'Öğrenci Belgesi'),
        ('CALISMA_IZNI', 'Çalışma İzni'),
        ('IKAMET_BEYAN', 'İkamet Beyan Formu'),
    ]
    
    GENEL_EVRAKLAR = [
        ('DILEKCE', 'Dilekçe'),
        ('TERCUME', 'Tercüme Belgesi'),
        ('APOSTIL', 'Apostil'),
        ('VEKALETNAME', 'Vekaletname'),
        ('DIGER', 'Diğer'),
    ]
    
    kategori = models.ForeignKey(DokumanKategori, on_delete=models.CASCADE, null=True, blank=True)
    ad = models.CharField(max_length=100)
    kod = models.CharField(max_length=50, null=True, blank=True)
    aciklama = models.TextField(blank=True, null=True)
    zorunlu = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.kategori} - {self.ad}" if self.kategori else self.ad
    
    class Meta:
        verbose_name = "Doküman Tipi"
        verbose_name_plural = "Doküman Tipleri"
        ordering = ['kategori', 'ad']

class Dokuman(models.Model):
    musteri = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='dokumanlar')
    dokuman_tipi = models.ForeignKey(DokumanTipi, on_delete=models.PROTECT)
    dosya = models.FileField(upload_to='dokumanlar/')
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True)
    son_guncelleme = models.DateTimeField(auto_now=True)
    notlar = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.musteri} - {self.dokuman_tipi}"
    
    class Meta:
        verbose_name = "Doküman"
        verbose_name_plural = "Dokümanlar"

class BasvuruSureci(models.Model):
    BASVURU_TIPLERI = [
        ('VATANDASLIK', 'Vatandaşlık'),
        ('OTURMA_IZNI', 'Oturma İzni'),
    ]
    
    SUREC_DURUMLARI = [
        ('BASLANGIC', 'Başlangıç'),
        ('BELGE_TOPLAMA', 'Belge Toplama'),
        ('INCELEME', 'İnceleme'),
        ('RANDEVU_BEKLENIYOR', 'Randevu Bekleniyor'),
        ('BASVURU_YAPILDI', 'Başvuru Yapıldı'),
        ('TAMAMLANDI', 'Tamamlandı'),
        ('REDDEDILDI', 'Reddedildi'),
    ]
    
    musteri = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='basvuru_surecleri')
    basvuru_tipi = models.CharField(max_length=50, choices=BASVURU_TIPLERI)
    baslangic_tarihi = models.DateTimeField(auto_now_add=True)
    son_guncelleme = models.DateTimeField(auto_now=True)
    randevu_tarihi = models.DateTimeField(null=True, blank=True)
    durum = models.CharField(max_length=20, choices=SUREC_DURUMLARI, default='BASLANGIC')
    notlar = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.musteri} - {self.get_basvuru_tipi_display()}"
    
    def get_durum_color(self):
        return {
            'BASLANGIC': 'secondary',
            'BELGE_TOPLAMA': 'info',
            'INCELEME': 'primary',
            'RANDEVU_BEKLENIYOR': 'warning',
            'BASVURU_YAPILDI': 'info',
            'TAMAMLANDI': 'success',
            'REDDEDILDI': 'danger',
        }.get(self.durum, 'primary')
    
    class Meta:
        verbose_name = "Başvuru Süreci"
        verbose_name_plural = "Başvuru Süreçleri"
