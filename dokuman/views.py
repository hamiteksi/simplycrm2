from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Dokuman, DokumanTipi, BasvuruSureci
from musteri.models import Customer
from .forms import DokumanForm, BasvuruSureciForm

# Doküman yönetimi için view'ları ekliyorum

@login_required
def dokuman_listesi(request, musteri_id):
    musteri = get_object_or_404(Customer, id=musteri_id)
    dokumanlar = Dokuman.objects.filter(musteri=musteri)
    return render(request, 'dokuman/dokuman_listesi.html', {
        'musteri': musteri,
        'dokumanlar': dokumanlar
    })

@login_required
def dokuman_yukle(request, musteri_id):
    musteri = get_object_or_404(Customer, id=musteri_id)
    if request.method == 'POST':
        form = DokumanForm(request.POST, request.FILES)
        if form.is_valid():
            dokuman = form.save(commit=False)
            dokuman.musteri = musteri
            dokuman.save()
            messages.success(request, 'Doküman başarıyla yüklendi.')
            return redirect('musteri:customer_detail', pk=musteri_id)
    else:
        form = DokumanForm()
    
    dokumanlar = Dokuman.objects.filter(musteri=musteri).order_by('-yuklenme_tarihi')
    dokuman_tipleri = DokumanTipi.objects.all()
    
    return render(request, 'dokuman/dokuman_yukle.html', {
        'musteri': musteri,
        'form': form,
        'dokumanlar': dokumanlar,
        'dokuman_tipleri': dokuman_tipleri,
    })

@login_required
def dokuman_guncelle(request, dokuman_id):
    dokuman = get_object_or_404(Dokuman, id=dokuman_id)
    if request.method == 'POST':
        form = DokumanForm(request.POST, request.FILES, instance=dokuman)
        if form.is_valid():
            form.save()
            messages.success(request, 'Doküman başarıyla güncellendi.')
            return redirect('dokuman:dokuman_listesi', musteri_id=dokuman.musteri.id)
    else:
        form = DokumanForm(instance=dokuman)
    return render(request, 'dokuman/dokuman_guncelle.html', {
        'form': form,
        'dokuman': dokuman
    })

@login_required
def basvuru_sureci_listesi(request, musteri_id):
    musteri = get_object_or_404(Customer, id=musteri_id)
    surecler = BasvuruSureci.objects.filter(musteri=musteri)
    return render(request, 'dokuman/basvuru_sureci_listesi.html', {
        'musteri': musteri,
        'surecler': surecler
    })

@login_required
def basvuru_sureci_olustur(request, musteri_id):
    musteri = get_object_or_404(Customer, id=musteri_id)
    if request.method == 'POST':
        form = BasvuruSureciForm(request.POST)
        if form.is_valid():
            surec = form.save(commit=False)
            surec.musteri = musteri
            surec.save()
            messages.success(request, 'Başvuru süreci başarıyla oluşturuldu.')
            return redirect('musteri:customer_detail', pk=musteri_id)
    else:
        form = BasvuruSureciForm()
    return render(request, 'dokuman/basvuru_sureci_olustur.html', {
        'form': form,
        'musteri': musteri
    })

@login_required
def basvuru_sureci_guncelle(request, surec_id):
    surec = get_object_or_404(BasvuruSureci, id=surec_id)
    if request.method == 'POST':
        form = BasvuruSureciForm(request.POST, instance=surec)
        if form.is_valid():
            form.save()
            messages.success(request, 'Başvuru süreci başarıyla güncellendi.')
            return redirect('musteri:customer_detail', pk=surec.musteri.id)
    else:
        form = BasvuruSureciForm(instance=surec)
    return render(request, 'dokuman/basvuru_sureci_guncelle.html', {
        'form': form,
        'surec': surec
    })
