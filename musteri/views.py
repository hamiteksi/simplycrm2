from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Customer, Yapilacak, Note
from dokuman.models import Dokuman, DokumanTipi, BasvuruSureci
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, DateField, F, Count, Sum
from django.db.models.functions import Cast, TruncMonth, TruncDate
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.http import FileResponse, HttpResponseRedirect, JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.utils import timezone
import json
import requests
from tabula.io import read_pdf
import pandas as pd
from bs4 import BeautifulSoup
from io import BytesIO
import urllib.parse
from openpyxl import Workbook
from datetime import date, timedelta
from itertools import groupby
from django_tables2 import RequestConfig
from .ptt_track import ptt_track

from .models import Customer, CustomerFile, Note, Communication, Yapilacak, CalendarEvent, ExpenseItem, Payment
from dokuman.models import Dokuman, DokumanTipi, BasvuruSureci
from .forms import (
    CustomerForm, CustomerQueryForm, 
    ExpenseForm, CalculateExpensesForm, CustomerFileForm, 
    YapilacakForm, NoteForm
)
from .tables import CustomerTable

# Dashboard View
@login_required
def dashboard(request):
    total_customers = Customer.objects.count()
    active_tasks = Yapilacak.objects.filter(tamamlandi=False).count()
    
    pending_tasks = Yapilacak.objects.filter(tamamlandi=False).order_by('son_tarih')[:5]
    completed_tasks = Yapilacak.objects.filter(tamamlandi=True).order_by('-updated_at')[:5]
    recent_customers = Customer.objects.all().order_by('-created_at')[:5]
    customers = Customer.objects.all()
    
    # Yaklaşan etkinlikler
    upcoming_events = CalendarEvent.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')[:5]
    
    # Monthly statistics
    today = timezone.now()
    six_months_ago = today - timezone.timedelta(days=180)
    monthly_stats = []
    
    for i in range(6):
        month_start = today - timezone.timedelta(days=30 * i)
        month_end = month_start - timezone.timedelta(days=30)
        count = Customer.objects.filter(created_at__gte=month_end, created_at__lt=month_start).count()
        monthly_stats.append({
            'month': month_end,
            'count': count
        })
    
    monthly_stats.reverse()
    
    return render(request, 'dashboard.html', {
        'total_customers': total_customers,
        'active_tasks': active_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'recent_customers': recent_customers,
        'monthly_stats': monthly_stats,
        'customers': customers,
        'upcoming_events': upcoming_events,
    })

# Profile Views
@login_required
def profile_view(request):
    return render(request, 'musteri/profile.html', {
        'user': request.user
    })

@login_required
def settings_view(request):
    return render(request, 'musteri/settings.html', {
        'user': request.user
    })

# Calendar View
@login_required
def calendar(request):
    # Get all tasks and format them for calendar
    tasks = Yapilacak.objects.all()
    calendar_events = []
    
    for task in tasks:
        calendar_events.append({
            'id': task.id,
            'title': task.yapilacak,
            'start': task.created_at.isoformat() if task.created_at else timezone.now().isoformat(),
            'end': task.tamamlanma_tarihi.isoformat() if task.tamamlanma_tarihi else None,
            'allDay': True,
            'className': 'bg-success' if task.tamamlandi else 'bg-warning'
        })
    
    context = {
        'calendar_events': json.dumps(calendar_events)
    }
    return render(request, 'calendar.html', context)

# Reports View
@login_required
def reports(request):
    # Get current date and 6 months ago
    today = timezone.now().date()
    six_months_ago = today - timezone.timedelta(days=180)
    
    # Customer data
    customers = Customer.objects.filter(created_at__date__gte=six_months_ago)
    customer_data = []
    customer_labels = []
    for i in range(6):
        month = today - timezone.timedelta(days=30*i)
        count = customers.filter(created_at__date__month=month.month).count()
        customer_data.append(count)
        customer_labels.append(month.strftime('%B'))
    customer_labels.reverse()
    customer_data.reverse()
    
    # Task data
    completed_tasks = Yapilacak.objects.filter(tamamlandi=True).count()
    pending_tasks = Yapilacak.objects.filter(tamamlandi=False).count()
    
    # Expense data
    expenses = ExpenseItem.objects.filter(created_at__date__gte=six_months_ago)
    expense_data = []
    expense_labels = []
    for i in range(6):
        month = today - timezone.timedelta(days=30*i)
        amount = expenses.filter(created_at__date__month=month.month).aggregate(total=Sum('amount'))['total'] or 0
        expense_data.append(float(amount))
        expense_labels.append(month.strftime('%B'))
    expense_labels.reverse()
    expense_data.reverse()
    
    # Document data
    valid_documents = CustomerFile.objects.filter(
        expiry_date__gt=today + timezone.timedelta(days=30)
    ).count()
    expiring_documents = CustomerFile.objects.filter(
        expiry_date__range=[today, today + timezone.timedelta(days=30)]
    ).count()
    expired_documents = CustomerFile.objects.filter(
        expiry_date__lt=today
    ).count()
    
    context = {
        'customer_count': Customer.objects.count(),
        'task_count': pending_tasks,
        'expense_total': ExpenseItem.objects.aggregate(total=Sum('amount'))['total'] or 0,
        'document_count': CustomerFile.objects.count(),
        'customer_labels': customer_labels,
        'customer_data': customer_data,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'expense_labels': expense_labels,
        'expense_data': expense_data,
        'valid_documents': valid_documents,
        'expiring_documents': expiring_documents,
        'expired_documents': expired_documents,
    }
    return render(request, 'musteri/reports.html', context)

# Task Views
@login_required
def yapilacak_list(request):
    tasks = Yapilacak.objects.all().order_by('-created_at')
    customers = Customer.objects.all()
    return render(request, 'musteri/yapilacak_list.html', {
        'tasks': tasks,
        'customers': customers
    })

@login_required
def add_yapilacak(request):
    if request.method == 'POST':
        yapilacak = request.POST.get('yapilacak')
        customer_id = request.POST.get('customer')
        
        task = Yapilacak(yapilacak=yapilacak)
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                task.customer = customer
            except Customer.DoesNotExist:
                pass
        task.save()
        
        messages.success(request, 'Task added successfully.')
        return redirect('musteri:yapilacak')
    return redirect('musteri:yapilacak')

@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Yapilacak, id=task_id)
        task.tamamlandi = not task.tamamlandi
        task.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# Deal Views
@login_required
def deal_list(request):
    return render(request, 'deals/list.html')

@login_required
def deal_create(request):
    return render(request, 'deals/create.html')

# Customer Views (renamed for consistency)
@login_required
def customer_list(request):
    return customer_list_view(request)

@login_required
def customer_create(request):
    return customer_create_view(request)

@csrf_exempt
def complete_yapilacak(request, id):
    if request.method == "POST":
        yapilacak = get_object_or_404(Yapilacak, id=id)
        yapilacak.tamamlandi = True
        yapilacak.tamamlanma_tarihi = timezone.now()  # Update completion time
        yapilacak.save()
        return JsonResponse({"success": True}, status=200)
    else:
        return JsonResponse({"success": False}, status=400)

@csrf_exempt
def add_yapilacak(request):
    if request.method == "POST":
        baslik = request.POST.get("yapilacak")
        aciklama = request.POST.get("detay")
        customer_id = request.POST.get("customer_id")
        son_tarih = timezone.now() + timezone.timedelta(days=7)  # Varsayılan olarak 1 hafta sonra
        
        try:
            customer = Customer.objects.get(id=customer_id) if customer_id else None
            new_item = Yapilacak(
                customer=customer,
                baslik=baslik,
                aciklama=aciklama,
                son_tarih=son_tarih
            )
            new_item.save()
            return JsonResponse({"success": True}, status=200)
        except Customer.DoesNotExist:
            return JsonResponse({"error": "Müşteri bulunamadı"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"success": False}, status=400)

def yapilacak_list_view(request):
    if request.method == "POST":
        form = YapilacakForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('yapilacak')
    else:
        form = YapilacakForm()
    yapilacaklar = Yapilacak.objects.all()
    return render(request, 'musteri/yapilacak_list.html', {'form': form, 'yapilacaklar': yapilacaklar})

class ExpenseCreateView(View):
    def get(self, request):
        form = ExpenseForm()
        return render(request, 'musteri/add_expense.html', {'form': form})

    def post(self, request):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('musteri:expense_list')  # Assuming you have an expense_list view to redirect
        return render(request, 'musteri/add_expense.html', {'form': form})

def calculate_expenses(request):
    total_expense = 0
    residence_card_fee = ExpenseItem.objects.get(name='residence_card').amount
    doviz_kuru = float(ExpenseItem.objects.get(name='doviz_kuru').amount)

    if request.method == 'POST':
        form = CalculateExpensesForm(request.POST)
        

        if form.is_valid():
            insurance_age_bracket = form.cleaned_data['insurance_age_bracket']
            country = form.cleaned_data['country']
            duration = form.cleaned_data['duration']
            

            if duration == 1:
                total_expense += insurance_age_bracket.fee_first
                total_expense += country.fee_first_year * doviz_kuru
                total_expense += (11 * country.fee_next_year) * doviz_kuru
            elif duration == 2:
                total_expense += insurance_age_bracket.fee_second
                total_expense += country.fee_first_year * doviz_kuru
                total_expense += (23 * country.fee_next_year) * doviz_kuru
                print(total_expense)
            
            if form.cleaned_data['residence_card']:
                total_expense += residence_card_fee

            for expense_item in ExpenseItem.objects.exclude(name='residence_card'):
                if form.cleaned_data[expense_item.name]:
                    total_expense += expense_item.fee

    else:
        form = CalculateExpensesForm()


    return render(request, 'musteri/calculate_expenses.html', {'form': form, 'total_expense': total_expense, 'residence_card_fee': residence_card_fee, 'doviz_kuru': doviz_kuru})

def customer_expiry_list(request):
    # bugünün tarihini al
    today = date.today()

    # iki ay sonrasına denk gelen gün sayısını hesapla (ortalama olarak bir ayın 30 gün olduğunu kabul ediyoruz)
    two_months_later = today + timedelta(days=60)

    # bugünden iki ay sonrası arasında bir residence_permit_end_date'e sahip olan müşterileri filtrele
    customers = Customer.objects.filter(
        residence_permit_end_date__gte=today, 
        residence_permit_end_date__lte=two_months_later
    ).order_by('first_name', 'last_name', 'residence_permit_end_date')

    # müşterileri belirli alanlara göre gruplandır ve her gruptan sadece bir tanesini al
    customers = [next(g) for k, g in groupby(customers, key=lambda x: (x.first_name, x.last_name, x.residence_permit_end_date))]

    return render(request, 'musteri/customer_expiry_list.html', {'customers': customers})

# def download_excel(request):
    # bugünün tarihini al
    today = date.today()

    # iki ay sonrasına denk gelen gün sayısını hesapla (ortalama olarak bir ayın 30 gün olduğunu kabul ediyoruz)
    two_months_later = today + timedelta(days=60)

    # bugünden iki ay sonrası arasında bir residence_permit_end_date'e sahip olan müşterileri filtrele
    customers = Customer.objects.filter(
        residence_permit_end_date__gte=today, 
        residence_permit_end_date__lte=two_months_later
    ).order_by('first_name', 'last_name', 'residence_permit_end_date')

    # müşterileri belirli alanlara göre gruplandır ve her gruptan sadece bir tanesini al
    customers = [next(g) for k, g in groupby(customers, key=lambda x: (x.first_name, x.last_name, x.residence_permit_end_date))]

    # her bir customer objesini belirli alanları içeren bir sözlüğe çeviriyoruz
    customers = [{
        'first_name': customer.first_name, 
        'last_name': customer.last_name, 
        'residence_permit_end_date': customer.residence_permit_end_date
    } for customer in customers]

        # Create a workbook and add a worksheet
    wb = Workbook()
    ws = wb.active

    # Add a header to the worksheet
    headers = ['First Name', 'Last Name', 'Residence Permit End Date']
    ws.append(headers)

    # Add the customers data to the worksheet
    for customer in customers:
        ws.append([
            customer['first_name'],
            customer['last_name'],
            customer['residence_permit_end_date']
        ])

    # Create a BytesIO object and save the workbook to it
    f = BytesIO()
    wb.save(f)

    # Create a HttpResponse with the xlsx file type
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    # Set the content disposition to attachment so it prompts the user to download
    response['Content-Disposition'] = 'attachment; filename=Expiring_Residence_Permits.xlsx'

    return response

def customer_status_list(request):
    # "Tamamlandı" durumunu hariç tutarak belirli durumları filtrele
    customers = Customer.objects.filter(
        status__in=['basvuru_yapildi', 'dosyalar_verildi', 'ptt_bekleniyor', 'kart_alindi']
    ).order_by('status')

    return render(request, 'musteri/customer_status_list.html', {'customers': customers})

def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('musteri:customer_list')  # listeleme view'ine yönlendir
    else:
        form = CustomerForm()
    return render(request, 'musteri/customer_form.html', {'form': form})

def add_note_to_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Note.objects.create(
                customer=customer,
                content=content
            )
            messages.success(request, 'Not başarıyla eklendi.')
    return redirect('musteri:customer_detail', pk=pk)

@login_required
def customer_list_view(request):
    # Filtreleme ve sıralama parametrelerini al
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-created_at')
    status_filter = request.GET.get('status', '')
    
    # Temel sorgu
    customers = Customer.objects.all()
    
    # Arama filtresi
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(application_number__icontains=search_query)
        )
    
    # Durum filtresi
    if status_filter:
        customers = customers.filter(status=status_filter)
    
    # Sıralama
    customers = customers.order_by(sort_by)
    
    # Tablo oluştur
    table = CustomerTable(customers)
    
    context = {
        'table': table,
        'search_query': search_query,
        'sort_by': sort_by,
        'status_filter': status_filter,
        'status_choices': Customer.STATUS_CHOICES,
    }
    
    return render(request, 'musteri/customer_list.html', context)

def customer_edit_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('musteri:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'musteri/customer_form.html', {'form': form})

def upload_pdf_view(request):
    if request.method == 'POST':
        pdf_file = request.FILES['document']
        fs = FileSystemStorage()
        # Dosya adını URL'den çözümle ve özel karakterleri çıkar
        filename = urllib.parse.unquote(pdf_file.name.replace(" ", "_"))
        filename = fs.save(filename, pdf_file)
        file_url = fs.url(filename)
        process_pdf(file_url)
        return redirect('musteri:customer_list')

    return render(request, 'musteri/upload_pdf.html')

def process_pdf(file_path):
    print(settings.MEDIA_ROOT)
    full_file_path = settings.MEDIA_ROOT + file_path[6:]

    # Tablo koordinatlarını tanımlıyoruz
    table_coordinates = [
        {'top': 104.5453, 'left': 20.5866, 'height': 138.4017, 'width': 556.5831, 'page': 1},
        {'top': 243.6911, 'left': 19.8425, 'height': 176.3505, 'width': 554.3508, 'page': 1},
        {'top': 431.9471, 'left': 22.8189, 'height': 59.5276, 'width': 554.3508, 'page': 1},
        {'top': 109.0099, 'left': 20.5866, 'height': 74.4095, 'width': 558.0713, 'page': 2},
        {'top': 190.8604, 'left': 25.7953, 'height': 132.4489, 'width': 552.1185, 'page': 2},
    ]

    # PDF'den tabloları oku
    tables = []
    for i, coord in enumerate(table_coordinates):
        print(f"Tablo {i+1} okunuyor...")
        table = read_pdf(
            full_file_path,
            pages=coord['page'],
            area=[coord['top'], coord['left'], coord['top'] + coord['height'], coord['left'] + coord['width']],
            multiple_tables=False,
            lattice=True,
            java_options=['-Dfile.encoding=UTF8', '-Xms128m', '-Xmx512m'],
            encoding='cp1254'
        )
        if table and len(table) > 0:
            tables.append(table[0])
            print(f"Tablo {i+1} başarıyla okundu")
            print(table[0])
        else:
            print(f"Tablo {i+1} okunamadı veya boş")

    def parse_date(date_str):
        if pd.isna(date_str):
            return None
        try:
            print(f"Tarih ayrıştırılıyor: {date_str}")
            date_str = str(date_str).strip()
            
            # Eğer tarih "/" içeriyorsa ve birden fazla tarih varsa (örn: 15.3.2017 / 13.3.2025)
            if ' / ' in date_str:
                # İlk tarihi al
                date_str = date_str.split(' / ')[0]
            
            # Farklı tarih formatlarını kontrol et
            if '/' in date_str:
                parts = date_str.replace(' ', '').split('/')
                if len(parts) == 3:
                    day, month, year = map(int, parts)
                    print(f"/ ile ayrıştırıldı: gün={day}, ay={month}, yıl={year}")
            elif '.' in date_str:
                parts = date_str.replace(' ', '').split('.')
                if len(parts) == 3:
                    day, month, year = map(int, parts)
                    print(f". ile ayrıştırıldı: gün={day}, ay={month}, yıl={year}")
            else:
                print("Geçersiz tarih formatı")
                return None
            
            # 2 haneli yıl kontrolü
            if year < 100:
                year += 2000 if year < 24 else 1900
            
            result = f"{year}-{month:02d}-{day:02d}"
            print(f"Sonuç tarih: {result}")
            return result
        except Exception as e:
            print(f"Tarih ayrıştırma hatası: {e}")
            return None

    # Veri sözlüğünü oluştur
    data = {}
    if len(tables) >= 3:
        print("Veriler okunuyor...")
        
        # Her tablonun içeriğini yazdır
        for i, table in enumerate(tables):
            print(f"\nTablo {i+1} içeriği:")
            print(table)
            print("\nSütun isimleri:")
            print(table.columns)
        
        data = {
            'application_date': parse_date(tables[0].iloc[0, 0] if len(tables) > 0 and len(tables[0]) > 0 else None),
            'application_number': tables[0].iloc[0, 3] if len(tables) > 0 and len(tables[0]) > 0 else None,
            'application_type': tables[0].iloc[1, 0] if len(tables) > 0 and len(tables[0]) > 0 else None,
            'appointment_place': tables[0].iloc[1, 3] if len(tables) > 0 and len(tables[0]) > 0 else None,
            'residence_type': tables[0].iloc[2, 0] if len(tables) > 0 and len(tables[0]) > 0 else None,
            'residence_permit_start_date': parse_date(tables[0].iloc[3, 0] if len(tables) > 0 and len(tables[0]) > 0 else None),
            'residence_permit_end_date': parse_date(tables[0].iloc[3, 3] if len(tables) > 0 and len(tables[0]) > 0 else None),
            'last_name': tables[1].iloc[1, 1] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'first_name': tables[1].iloc[2, 1] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'nationality': tables[1].iloc[0, 3] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'date_of_birth': parse_date(tables[1].iloc[7, 3] if len(tables) > 1 and len(tables[1]) > 0 else None),
            'identity_number': tables[1].iloc[6, 1] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'father_name': tables[1].iloc[4, 1] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'mother_name': tables[1].iloc[5, 1] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'gender': tables[1].iloc[5, 3] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'marital_status': tables[1].iloc[6, 3] if len(tables) > 1 and len(tables[1]) > 0 else None,
            'passport_type': tables[2].iloc[1, 0] if len(tables) > 2 and len(tables[2]) > 0 else None,
            'passport_number': tables[2].iloc[1, 3] if len(tables) > 2 and len(tables[2]) > 0 else None,
            'passport_date': parse_date(tables[2].iloc[2, 0] if len(tables) > 2 and len(tables[2]) > 0 else None),
            'issuing_authority': tables[2].iloc[2, 3] if len(tables) > 2 and len(tables[2]) > 0 else None,
            'address': tables[3].iloc[0, 0] if len(tables) > 3 and len(tables[3]) > 0 else None,
            'phone': tables[3].iloc[0, 3] if len(tables) > 3 and len(tables[3]) > 0 else None,
            'email': tables[3].iloc[1, 3] if len(tables) > 3 and len(tables[3]) > 0 else None,
            'income': tables[4].iloc[0, 0] if len(tables) > 4 and len(tables[4]) > 0 else None,
            'income_source': tables[4].iloc[0, 3] if len(tables) > 4 and len(tables[4]) > 0 else None,
            'job': tables[4].iloc[1, 0] if len(tables) > 4 and len(tables[4]) > 0 else None,
            'insurance_type': tables[4].iloc[3, 0] if len(tables) > 4 and len(tables[4]) > 0 else None,
        }

        print("\nOkunan veriler:")
        for key, value in data.items():
            print(f"{key}: {value}")

    # Boş değerleri temizle
    data = {k: v for k, v in data.items() if v is not None and str(v).strip() != ''}
    
    create_customer(data)
    return data


def create_customer(data):
    # Tarihleri datetime formatına çevir
    from datetime import datetime

    def convert_date(date_str):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return None

    customer = Customer(
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        identity_number=data.get('identity_number', ''),
        nationality=data.get('nationality', ''),
        father_name=data.get('father_name', ''),
        mother_name=data.get('mother_name', ''),
        job=data.get('job', ''),
        gender=data.get('gender', ''),
        passport_type=data.get('passport_type', ''),
        address=data.get('address', ''),
        income=data.get('income', ''),
        income_source=data.get('income_source', ''),
        insurance_type=data.get('insurance_type', ''),
        date_of_birth=convert_date(data.get('date_of_birth')),
        marital_status=data.get('marital_status', ''),
        passport_number=data.get('passport_number', ''),
        issuing_authority=data.get('issuing_authority', ''),
        passport_date=convert_date(data.get('passport_date')),
        application_type=data.get('application_type', ''),
        residence_type=data.get('residence_type', ''),
        residence_permit_start_date=convert_date(data.get('residence_permit_start_date')),
        residence_permit_end_date=convert_date(data.get('residence_permit_end_date')),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        application_number=data.get('application_number', ''),
        application_date=convert_date(data.get('application_date')),
        appointment_place=data.get('appointment_place', ''),
        service_type=data.get('service_type', ''),
    )
    customer.save()

# last_check_update view'ınızı güncelliyorum
@login_required
def last_check_update(request, customer_id):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, id=customer_id)
        customer.last_check_date = timezone.now()
        customer.save()
        messages.success(request, 'Son kontrol tarihi güncellendi.')
        return redirect('musteri:customer_detail', pk=customer_id)
    return redirect('musteri:customer_detail', pk=customer_id)

@login_required
def customer_detail_view(request, pk):
    main_customer = get_object_or_404(Customer, pk=pk)
    notes = Note.objects.filter(customer=main_customer).order_by('-created_at')
    customer_files = CustomerFile.objects.filter(customer=main_customer)
    basvuru_surecleri = BasvuruSureci.objects.filter(musteri=main_customer).order_by('-baslangic_tarihi')
    contact_history = Communication.objects.filter(customer=main_customer).order_by('-date')
    
    # Doküman tipleri ve dokümanlar
    dokuman_tipleri = DokumanTipi.objects.all()
    dokumanlar = Dokuman.objects.filter(musteri=main_customer).order_by('-yuklenme_tarihi')
    
    # Ödemeler
    payments = Payment.objects.filter(customer=main_customer).order_by('-date')
    
    # Tasks
    tasks = Yapilacak.objects.filter(customer=main_customer).order_by('-created_at')
    
    # Etkinlikler
    calendar_events = CalendarEvent.objects.filter(customer=main_customer).order_by('start_time')
    
    context = {
        'main_customer': main_customer,
        'notes': notes,
        'customer_files': customer_files,
        'basvuru_surecleri': basvuru_surecleri,
        'contact_history': contact_history,
        'dokuman_tipleri': dokuman_tipleri,
        'dokumanlar': dokumanlar,
        'payments': payments,
        'tasks': tasks,
        'calendar_events': calendar_events,
    }
    
    return render(request, 'musteri/customer_detail.html', context)

def delete_note(request, pk, note_id):
    Note.objects.filter(id=note_id, customer_id=pk).delete()
    return HttpResponseRedirect(reverse('musteri:customer_detail', args=[pk]))

def customer_delete_view(request, pk):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, pk=pk)
        customer.delete()
        messages.success(request, "Müşteri kaydı başarıyla silindi.")
        return redirect('musteri:customer_list')

def customer_query_view(request):
    if request.method == 'POST':
        form = CustomerQueryForm(request.POST)
        if form.is_valid():
            application_number = form.cleaned_data['application_number']
            phone_number = form.cleaned_data['phone_number']
            try:
                customer = Customer.objects.get(application_number=application_number, phone_number=phone_number)
                return redirect('musteri:customer_detail', pk=customer.pk)
            except Customer.DoesNotExist:
                form.add_error(None, 'Bu başvuru numarası ve telefon numarasına sahip bir müşteri bulunamadı')
    else:
        form = CustomerQueryForm()
    return render(request, 'musteri/customer_query.html', {'form': form})


class PTTTrackingView(View):
    def get(self, request, *args, **kwargs):
        tracking_code = request.GET.get("ptt_code", None)
        print(tracking_code)
        if tracking_code:
            tracking_result = ptt_track(
                tracking_code
            )  # ptt_track fonksiyonunu burada çağırıyoruz
            tracking_result_list = tracking_result.split(
                "\n"
            )  # string'i '\n' karakterine göre böler
            return JsonResponse(
                tracking_result_list, safe=False
            )  # JsonResponse'a bir liste veriyoruz
        else:
            return JsonResponse({"error": "Invalid tracking code."})

def home(request):
    return render(request, 'musteri/home.html')

class FormView:
    def __init__(self):
        # Burada bir oturum oluşturduk
        self.session = requests.Session()
        self.captcha_session = None  # Captcha oturumunu saklayacak bir değişken oluşturduk

    def captcha(self, *args):
        url = "https://e-ikamet.goc.gov.tr/Ikamet/DevamEdenBasvuruGiris"
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'Host': 'e-ikamet.goc.gov.tr',
            'Origin': 'https://e-ikamet.goc.gov.tr',
            'Referer': 'https://e-ikamet.goc.gov.tr/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = self.session.post(url, headers=headers)
        token = self.session.post('https://e-ikamet.goc.gov.tr/Ikamet/DevamEdenBasvuruGiris', headers=headers)
        print('/bu captcha session', self.session.cookies.get_dict())

        soup = BeautifulSoup(response.content, 'html.parser')
        koup = BeautifulSoup(token.content, 'html.parser')
        img_tag = soup.find('img', id='CaptchaImage')
        captcha_url = img_tag.get('src') if img_tag else None
        base_url = "https://e-ikamet.goc.gov.tr"
        if captcha_url and not captcha_url.startswith("http"):
            captcha_url = base_url + captcha_url
        response = self.session.get(captcha_url, headers=headers)

        captcha_de_text = soup.find('input', {'name': 'CaptchaDeText'})['value']
        print('captcha: ', captcha_de_text)
        request_verification_token = soup.find('input', {'name': '__RequestVerificationToken'})['value']
        print('request: ', request_verification_token)
        captcha_image = FileResponse(BytesIO(response.content), content_type='image/gif')
        return captcha_image


    def form_view(self, request):
        print('/bu form session', self.session.cookies.get_dict())
        captcha_image= self.captcha()
        # captcha_image = captcha_image.streaming_content  # captcha_image'i tuple'dan alınan değere atayın

        # captcha_image = captcha_response.capctcha_image
        # captcha_de_text = captcha_response['captcha_de_text']
        # request_verification_token = captcha_response['request_verification_token']
        if request.method == 'POST':
            form = BasvuruForm(request.POST)
            if form.is_valid():
                basvuru_no = form.cleaned_data['basvuru_no']
                email_or_phone = form.cleaned_data['email_or_phone']
                yabanci_kimlik_no = form.cleaned_data['yabanci_kimlik_no']
                captcha_input = form.cleaned_data['captcha_input']
                captchaDeText = form.cleaned_data['captchaDeText']
                pasaportBelgeNo = form.cleaned_data['pasaport']
                cepTelefon = form.cleaned_data['telefon']

                data = {
                    'basvuruNo': basvuru_no,
                    'EPosta': email_or_phone,
                    "cepTelefon":pasaportBelgeNo,
                    'yabanciKimlikNo': yabanci_kimlik_no,
                    'CaptchaInputText': captcha_input,
                    "pasaportBelgeNo":cepTelefon,
                    "islemTur":-1,
                    # 'CaptchaDeText': captcha_de_text,
                    'CaptchaDeText': captchaDeText,
                    'devamEdebilir': True,


                }
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': '*/*',
                    'Accept-Language': 'tr-TR,tr;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'keep-alive',
                }

                response = self.session.post('https://e-ikamet.goc.gov.tr/Ikamet/DevamEdenBasvuruGiris/Ara', headers=headers, json=data)
                print('BURASI RESPOOOOONSE', response.json())
                print(data)
                return render(request, 'musteri/response.html', {'form': form, 'response': response.json()})
        else:
            form = BasvuruForm()
            captcha_image= self.captcha(request)
            print('/bu form session', self.session.cookies.get_dict())
            # print('buda content:', captcha_image.streaming_content)

        return render(request, 'musteri/ikamet.html', {'form': form, 'captcha_image': captcha_image })

# Calendar Views
@login_required
def calendar_view(request):
    customers = Customer.objects.all()
    events = []
    calendar_events = CalendarEvent.objects.all()
    for event in calendar_events:
        events.append({
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'id': event.id,
            'description': event.description
        })
    return render(request, 'musteri/calendar.html', {
        'customers': customers,
        'events': json.dumps(events)
    })

@login_required
def calendar_events_view(request):
    events = []
    
    # Add calendar events
    calendar_events = CalendarEvent.objects.all()
    for event in calendar_events:
        events.append({
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'description': event.description,
            'id': event.id
        })
    
    return JsonResponse(events, safe=False)

@login_required
def calendar_event_create_view(request):
    if request.method == 'POST':
        data = request.POST
        customer_id = data.get('customer_id')
        try:
            customer = Customer.objects.get(id=customer_id) if customer_id else None
            
            # Tarihleri datetime'a çevir
            from datetime import datetime
            start_time = datetime.fromisoformat(data.get('start').replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data.get('end').replace('Z', '+00:00')) if data.get('end') else start_time
            
            event = CalendarEvent.objects.create(
                customer=customer,
                title=data.get('title'),
                description=data.get('description', ''),
                start_time=start_time,
                end_time=end_time
            )
            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'description': event.description
            })
        except Customer.DoesNotExist:
            return JsonResponse({'error': 'Müşteri bulunamadı'}, status=404)
        except ValueError as e:
            return JsonResponse({'error': f'Tarih formatı hatalı: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def calendar_event_delete_view(request, event_id):
    if request.method == 'POST':
        try:
            event = CalendarEvent.objects.get(id=event_id)
            event.delete()
            return JsonResponse({'status': 'success'})
        except CalendarEvent.DoesNotExist:
            return JsonResponse({'error': 'Etkinlik bulunamadı'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

# Report Views
def reports_view(request):
    return render(request, 'musteri/reports.html')

def customer_reports_view(request):
    return render(request, 'musteri/customer_reports.html')

def task_reports_view(request):
    return render(request, 'musteri/task_reports.html')

def expense_reports_view(request):
    return render(request, 'musteri/expense_reports.html')

# Expense Views
def expense_view(request):
    return render(request, 'musteri/expense.html')

def expense_create_view(request):
    return render(request, 'musteri/expense_create.html')

def expense_edit_view(request, pk):
    return render(request, 'musteri/expense_edit.html')

def expense_delete_view(request, pk):
    return render(request, 'musteri/expense_delete.html')

# Customer Documents & Status Views
def customer_documents_view(request):
    return render(request, 'musteri/customer_documents.html')

# Profile & Settings Views
def profile_view(request):
    return render(request, 'musteri/profile.html', {
        'user': request.user
    })

def settings_view(request):
    return render(request, 'musteri/settings.html', {
        'user': request.user
    })

def notification_settings_view(request):
    return render(request, 'musteri/notification_settings.html')

# API Views
def customer_search_api(request):
    return JsonResponse({'status': 'ok'})

def task_search_api(request):
    return JsonResponse({'status': 'ok'})

def dashboard_view(request):
    context = {
        'customer_count': Customer.objects.count(),
        'task_count': Yapilacak.objects.filter(tamamlandi=False).count(),
        'document_count': CustomerFile.objects.count(),
        'expense_count': ExpenseItem.objects.count(),
        'recent_customers': Customer.objects.order_by('-created_at')[:5],
        'pending_tasks': Yapilacak.objects.filter(tamamlandi=False).order_by('-created_at')[:5],
        'expiring_documents': CustomerFile.objects.filter(
            expiry_date__isnull=False,
            expiry_date__gte=timezone.now()
        ).order_by('expiry_date')[:5]
    }
    return render(request, 'musteri/dashboard.html', context)

@login_required
def add_payment(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        description = request.POST.get('description')
        
        if amount:
            from decimal import Decimal
            from datetime import datetime
            amount_decimal = Decimal(amount)
            
            # Ödemeyi kaydet
            Payment.objects.create(
                customer=customer,
                amount=amount_decimal,
                description=description,
                date=datetime.now()  # Şu anki tarihi ekle
            )
            
            # Toplam ödemeyi güncelle
            current_payment = customer.payment_made or Decimal('0')
            customer.payment_made = current_payment + amount_decimal
            customer.save()
            
            messages.success(request, f'{amount}₺ tutarında ödeme başarıyla eklendi.')
        
    return redirect('musteri:customer_detail', pk=customer_id)

@login_required
def calendar_event_detail_view(request, event_id):
    try:
        event = CalendarEvent.objects.get(id=event_id)
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'description': event.description
        })
    except CalendarEvent.DoesNotExist:
        return JsonResponse({'error': 'Etkinlik bulunamadı'}, status=404)

@login_required
def calendar_event_update_view(request, event_id):
    if request.method == 'POST':
        try:
            event = CalendarEvent.objects.get(id=event_id)
            data = request.POST
            
            # Tarihleri datetime'a çevir
            from datetime import datetime
            start_time = datetime.fromisoformat(data.get('start').replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data.get('end').replace('Z', '+00:00')) if data.get('end') else start_time
            
            event.title = data.get('title')
            event.description = data.get('description', '')
            event.start_time = start_time
            event.end_time = end_time
            event.save()
            
            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start_time.isoformat(),
                'end': event.end_time.isoformat(),
                'description': event.description
            })
        except CalendarEvent.DoesNotExist:
            return JsonResponse({'error': 'Etkinlik bulunamadı'}, status=404)
        except ValueError as e:
            return JsonResponse({'error': f'Tarih formatı hatalı: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)
