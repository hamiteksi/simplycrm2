from django.urls import path
from . import views

app_name = 'dokuman'

urlpatterns = [
    path('musteri/<int:musteri_id>/dokumanlar/', views.dokuman_listesi, name='dokuman_listesi'),
    path('musteri/<int:musteri_id>/dokuman/yukle/', views.dokuman_yukle, name='dokuman_yukle'),
    path('dokuman/<int:dokuman_id>/guncelle/', views.dokuman_guncelle, name='dokuman_guncelle'),
    path('musteri/<int:musteri_id>/basvuru-surecleri/', views.basvuru_sureci_listesi, name='basvuru_sureci_listesi'),
    path('musteri/<int:musteri_id>/basvuru-sureci/olustur/', views.basvuru_sureci_olustur, name='basvuru_sureci_olustur'),
    path('basvuru-sureci/<int:surec_id>/guncelle/', views.basvuru_sureci_guncelle, name='basvuru_sureci_guncelle'),
]
