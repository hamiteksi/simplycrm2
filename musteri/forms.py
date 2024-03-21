from django import forms
from .models import Customer,Expense, ExpenseItem, Country, InsuranceAgeBracket, CustomerFile, Yapilacak, Note


class YapilacakForm(forms.ModelForm):
    class Meta:
        model = Yapilacak
        fields = ['yapilacak', 'detay']


class CustomerFileForm(forms.ModelForm):
    class Meta:
        model = CustomerFile
        fields = ['uploaded_file', 'file_description']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['text']

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # Eğer 'notes' alanını kaldırdıysanız, fields listesinden de çıkarmalısınız.
        fields = ['first_name', 'last_name', 'identity_number', 'nationality', 'date_of_birth',
                  'marital_status', 'passport_number', 'issuing_authority', 'passport_date',
                  'application_type', 'residence_type', 'residence_permit_start_date',
                  'residence_permit_end_date', 'passport_info', 'service_type', 'ptt_code',
                  'phone_number', 'payment_made', 'communication_history', 'application_number',
                  'mail', 'status']
        widgets = {
            'residence_permit_start_date': forms.DateInput(attrs={'type': 'date'}),
            'residence_permit_end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CustomerQueryForm(forms.Form):
    application_number = forms.CharField(label='Başvuru Numarası')
    phone_number = forms.CharField(label='Telefon Numarası')



class BasvuruForm(forms.Form):
    basvuru_no = forms.CharField(label='Başvuru No', max_length=100)
    email_or_phone = forms.CharField(label='Email ya da Telefon', max_length=100)
    yabanci_kimlik_no = forms.CharField(label='Yabancı Kimlik No ya da Pasaport No', max_length=100)
    captcha_input = forms.CharField(label='CAPTCHA Girişi', max_length=100)
    captchaDeText = forms.CharField(label='captchaDeText', max_length=100)
    pasaport =  forms.CharField(label='pasaport', max_length=100)
    telefon = forms.CharField(label='telefon', max_length=100)


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['age', 'country', 'contract_fee', 'population_fee', 'card_fee']

class CalculateExpensesForm(forms.Form):
    insurance_age_bracket = forms.ModelChoiceField(
        queryset=InsuranceAgeBracket.objects.all(),
        label="Sigorta Yaş Aralığı",
        required=False,
        widget=forms.Select(attrs={'class': 'insurance_age_bracket'}),
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label="Ülke",
        required=False,
        widget=forms.Select(attrs={'class': 'country'}),
    )
    duration = forms.ChoiceField(
        choices=[(1, "1 Yıl"), (2, "2 Yıl")],
        label="Süre",
        initial=1,
        widget=forms.Select(attrs={'class': 'duration'}),
    )
    residence_card = forms.BooleanField(
        label="Ikamet Kartı",
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'residence_card'}),
    )

    def __init__(self, *args, **kwargs):
        super(CalculateExpensesForm, self).__init__(*args, **kwargs)
        expense_items = ExpenseItem.objects.all()
        for item in expense_items:
            self.fields[item.name] = forms.BooleanField(
                label=item.name,
                initial=False,
                required=False,
                widget=forms.CheckboxInput(attrs={'class': item.name})
            )
