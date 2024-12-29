from django.core.management.base import BaseCommand
from dokuman.models import DokumanKategori, DokumanTipi

class Command(BaseCommand):
    help = 'Varsayılan döküman kategorilerini ve tiplerini oluşturur'

    def handle(self, *args, **kwargs):
        # Kategorileri oluştur
        vatandaslik, created = DokumanKategori.objects.get_or_create(
            ad='VATANDASLIK',
            defaults={'aciklama': 'Vatandaşlık başvurusu için gerekli belgeler'}
        )
        self.stdout.write(f'{"Oluşturuldu" if created else "Zaten var"}: Vatandaşlık kategorisi')

        oturma_izni, created = DokumanKategori.objects.get_or_create(
            ad='OTURMA_IZNI',
            defaults={'aciklama': 'Oturma izni başvurusu için gerekli belgeler'}
        )
        self.stdout.write(f'{"Oluşturuldu" if created else "Zaten var"}: Oturma İzni kategorisi')

        genel, created = DokumanKategori.objects.get_or_create(
            ad='GENEL',
            defaults={'aciklama': 'Genel kullanım için belgeler'}
        )
        self.stdout.write(f'{"Oluşturuldu" if created else "Zaten var"}: Genel kategori')

        # Vatandaşlık belgeleri
        vatandaslik_evraklari = [
            ('PASAPORT', 'Pasaport', True),
            ('DOGUM_BELGESI', 'Doğum Belgesi', True),
            ('EVLILIK_BELGESI', 'Evlilik Belgesi', False),
            ('ADLI_SICIL', 'Adli Sicil Belgesi', True),
            ('SAGLIK_SIGORTASI', 'Sağlık Sigortası', True),
            ('BANKA_HESAP', 'Banka Hesap Dökümleri', True),
            ('TAPU', 'Tapu Belgesi', True),
            ('VERGI_NO', 'Vergi Numarası Belgesi', True),
            ('IKAMET_BELGESI', 'İkamet Belgesi', True),
            ('FOTOGRAF', 'Biyometrik Fotoğraf', True),
        ]

        for kod, ad, zorunlu in vatandaslik_evraklari:
            dokuman, created = DokumanTipi.objects.get_or_create(
                kategori=vatandaslik,
                kod=kod,
                defaults={
                    'ad': ad,
                    'zorunlu': zorunlu,
                    'aciklama': f'Vatandaşlık başvurusu için {ad.lower()}'
                }
            )
            self.stdout.write(f'{"Oluşturuldu" if created else "Zaten var"}: {ad}')

        # Oturma izni belgeleri
        oturma_izni_evraklari = [
            ('PASAPORT', 'Pasaport', True),
            ('FOTOGRAF', 'Biyometrik Fotoğraf', True),
            ('SAGLIK_SIGORTASI', 'Sağlık Sigortası', True),
            ('GELIR_BELGESI', 'Gelir Belgesi', True),
            ('KIRA_KONTRATI', 'Kira Kontratı', True),
            ('OGRENCI_BELGESI', 'Öğrenci Belgesi', False),
            ('CALISMA_IZNI', 'Çalışma İzni', False),
            ('IKAMET_BEYAN', 'İkamet Beyan Formu', True),
        ]

        for kod, ad, zorunlu in oturma_izni_evraklari:
            dokuman, created = DokumanTipi.objects.get_or_create(
                kategori=oturma_izni,
                kod=kod,
                defaults={
                    'ad': ad,
                    'zorunlu': zorunlu,
                    'aciklama': f'Oturma izni başvurusu için {ad.lower()}'
                }
            )
            self.stdout.write(f'{"Oluşturuldu" if created else "Zaten var"}: {ad}')

        # Genel belgeler
        genel_evraklar = [
            ('DILEKCE', 'Dilekçe', False),
            ('TERCUME', 'Tercüme Belgesi', False),
            ('APOSTIL', 'Apostil', False),
            ('VEKALETNAME', 'Vekaletname', False),
            ('DIGER', 'Diğer', False),
        ]

        for kod, ad, zorunlu in genel_evraklar:
            dokuman, created = DokumanTipi.objects.get_or_create(
                kategori=genel,
                kod=kod,
                defaults={
                    'ad': ad,
                    'zorunlu': zorunlu,
                    'aciklama': f'Genel kullanım için {ad.lower()}'
                }
            )
            self.stdout.write(f'{"Oluşturuldu" if created else "Zaten var"}: {ad}')
