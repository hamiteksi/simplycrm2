from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.db.models import Q, DateField, F
from django.db.models.functions import Cast
from .models import Customer, ExpenseItem, CustomerFile, Yapilacak
from .forms import CustomerForm, CustomerQueryForm, BasvuruForm, ExpenseForm, CalculateExpensesForm, CustomerFileForm, YapilacakForm
import tabula
import pandas as pd
from django.conf import settings
from django.http import JsonResponse, FileResponse
from django.views import View
from .ptt_track import ptt_track  # ptt_track isimli bir Python dosyası oluşturun ve PTT takip kodunuzu oraya taşıyın.
import requests
from bs4 import BeautifulSoup
from django.http import FileResponse, HttpResponse
from io import BytesIO
from datetime import date, timedelta
from django.utils import timezone
from itertools import groupby
from .tables import CustomerTable
from django_tables2 import RequestConfig
from django.views.decorators.csrf import csrf_exempt
import urllib.parse
from openpyxl import Workbook
from django.contrib.auth.decorators import login_required




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
        yapilacak = request.POST.get("yapilacak")
        detay = request.POST.get("detay")
        new_item = Yapilacak(yapilacak=yapilacak, detay=detay)
        new_item.save()
        return JsonResponse({"success": True}, status=200)
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


def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')  # listeleme view'ine yönlendir
    else:
        form = CustomerForm()
    return render(request, 'musteri/customer_form.html', {'form': form})

def customer_list_view(request):
    search_term = request.GET.get('search_term', '')

    customers = Customer.objects.filter(
        Q(first_name__icontains=search_term) | 
        Q(last_name__icontains=search_term) |
        Q(phone_number__icontains=search_term) |
        Q(application_number__icontains=search_term) |
        Q(passport_number__icontains=search_term) |
        Q(identity_number__icontains=search_term)

    ).order_by('-application_number')


    table = CustomerTable(customers)  # Use the filtered queryset here

    RequestConfig(request, paginate={'per_page': 10}).configure(table)
    # Get all uncompleted tasks
    yapilacaklar = Yapilacak.objects.filter(tamamlandi=False).order_by('-olusturulma_tarihi')

    # Get last 3 completed tasks
    completed_yapilacaklar = Yapilacak.objects.filter(tamamlandi=True).order_by('-tamamlanma_tarihi')[:3]

    return render(request, 'musteri/customer_list.html', {'table': table, 'yapilacaklar': yapilacaklar, 'completed_yapilacaklar': completed_yapilacaklar})

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
    full_file_path = settings.MEDIA_ROOT +  file_path[6:]
    tables = tabula.read_pdf(full_file_path, pages="1-2", lattice=True, multiple_tables=True)
    num_tables = len(tables)
    if num_tables > 8:
        first_table = tables[2]
        second_table = tables[0]
        third_table = tables[3]
        forth_table = tables[7]
    else:
        first_table = tables[0]
        second_table = tables[2]
    with pd.ExcelWriter(f'output3.xlsx') as writer:  
        if num_tables > 8:
            first_table.to_excel(writer, sheet_name='Sheet1')
            second_table.to_excel(writer, sheet_name='Sheet1', startrow=len(first_table)+1)
            third_table.to_excel(writer, sheet_name='Sheet1', startrow=len(first_table) + len(second_table) + 3, index=False)
            forth_table.to_excel(writer, sheet_name='Sheet1', startrow=len(first_table) + len(second_table) + 6, index=False)
        else:
            first_table.to_excel(writer, sheet_name='Sheet1', startrow=1, startcol=1, index=False)
            second_table.to_excel(writer, sheet_name='Sheet1', startrow=len(first_table) + 1, index=False)
            
    df = pd.read_excel("output3.xlsx")
    if num_tables > 8:
        data = {
            'soyadi': df.iloc[1, 2],
            'adi': df.iloc[2, 2],
            'kimlik_no': df.iloc[6, 2],
            'uyruk' : df.iloc[0, 4],
            'dogum' : df.iloc[7, 4],
            'medeni' : df.iloc[6, 4],
            'pasaport' : df.iloc[18, 4],
            'veren_makam' : df.iloc[19, 4],
            'pasaport_tarih' : df.iloc[19, 2],
            'basvuru_turu' : df.iloc[12, 3],
            'ikamet_turu' : df.iloc[14, 3],
            'baslangic' : df.iloc[15, 3],
            'bitis' : df.iloc[15, 6],
            'mail' : df.iloc[23, 5],
            'basvuru' : df.iloc[11, 6],
            'tel' : df.iloc[21, 5],
            # Daha fazla alanlar...
        }
    else:
        data = {
            'soyadi': df.iloc[7, 2],
            'adi': df.iloc[8, 2],
            'kimlik_no': df.iloc[12, 2],
            'uyruk' : df.iloc[6, 4],
            'dogum' : df.iloc[13, 4],
            'medeni' : df.iloc[12, 4],
            'pasaport' : df.iloc[18, 4],
            'veren_makam' : df.iloc[19, 4],
            'pasaport_tarih' : df.iloc[19, 2],
            'basvuru_turu' : df.iloc[1, 3],
            'ikamet_turu' : df.iloc[3, 3],
            'baslangic' : df.iloc[4, 3],
            'bitis' : df.iloc[4, 6],
            'mail' : df.iloc[36, 5],
            'basvuru' : df.iloc[0, 6],
            'telefon' : df.iloc[34, 5],
            # Daha fazla alanlar...
        }
    # TODO: Diğer alanları da oku ve bir sözlük oluştur
    create_customer(data)


def create_customer(data):
    customer = Customer(
        first_name=data.get('adi', ''),
        last_name=data.get('soyadi', ''),
        identity_number=data.get('kimlik_no', ''),
        nationality=data.get('uyruk', ''),
        # Tarihleri parse ediyoruz
        date_of_birth=pd.to_datetime(data.get('dogum'), errors='coerce'),
        marital_status=data.get('medeni', ''),
        passport_number=data.get('pasaport', ''),
        issuing_authority=data.get('veren_makam', ''),
        # Pasaport tarihini parse ediyoruz
        passport_date=pd.to_datetime(data.get('pasaport_tarih'), errors='coerce'),
        application_type=data.get('basvuru_turu', ''),
        residence_type=data.get('ikamet_turu', ''),
        # Tarihleri parse ediyoruz
        residence_permit_start_date=pd.to_datetime(data.get('baslangic'), errors='coerce'),
        residence_permit_end_date=pd.to_datetime(data.get('bitis'), errors='coerce'),
        phone_number=data.get('telefon', ''),
        mail=data.get('mail', ''),
        # 'basvuru' alanını nasıl işleyeceğinizi belirtmediniz, bu yüzden bu satırı yorumladım
        application_number=data.get('basvuru', ''),
    )
    customer.save()


def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    same_customers = Customer.objects.filter(first_name=customer.first_name, 
                                             last_name=customer.last_name, 
                                             passport_number=customer.passport_number)
    communication_history = customer.communication_history.all()

    if request.method == 'POST':
        form = CustomerFileForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = form.save(commit=False)
            new_file.customer = customer
            new_file.save()
            return redirect('musteri:customer_detail', pk=customer.pk)
    else:
        form = CustomerFileForm()

    context = {
        'main_customer': customer,
        'same_customers': same_customers,
        'communication_history': communication_history,
        'form': form,
    }

    return render(request, 'musteri/customer_detail.html', context)

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
