from django import forms
from .models import Dokuman, BasvuruSureci, DokumanTipi

class DokumanForm(forms.ModelForm):
    class Meta:
        model = Dokuman
        fields = ['dokuman_tipi', 'dosya', 'notlar']
        widgets = {
            'dokuman_tipi': forms.Select(attrs={'class': 'form-control'}),
            'dosya': forms.FileInput(attrs={'class': 'form-control'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'dokuman_tipi': 'Doküman Tipi',
            'dosya': 'Dosya',
            'notlar': 'Notlar',
        }
        help_texts = {
            'notlar': 'Doküman ile ilgili eklemek istediğiniz notları yazabilirsiniz.',
        }

class BasvuruSureciForm(forms.ModelForm):
    class Meta:
        model = BasvuruSureci
        fields = ['basvuru_tipi', 'randevu_tarihi', 'durum', 'notlar']
        widgets = {
            'basvuru_tipi': forms.Select(attrs={'class': 'form-control'}),
            'randevu_tarihi': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'durum': forms.Select(attrs={'class': 'form-control'}),
            'notlar': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'basvuru_tipi': 'Başvuru Tipi',
            'randevu_tarihi': 'Randevu Tarihi',
            'durum': 'Durum',
            'notlar': 'Notlar',
        }
        help_texts = {
            'randevu_tarihi': 'Randevu tarihi ve saatini seçiniz.',
            'notlar': 'Başvuru süreci ile ilgili notlarınızı yazabilirsiniz.',
        }
