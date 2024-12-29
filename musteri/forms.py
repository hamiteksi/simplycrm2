from django import forms
from django.forms import ModelForm, DateInput
from .models import Customer, CustomerFile, Note, Communication, Yapilacak, CalendarEvent, ExpenseItem, Payment, Expense, Country, InsuranceAgeBracket

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'customer_notes']
        widgets = {
            'customer_notes': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerFileForm(forms.ModelForm):
    class Meta:
        model = CustomerFile
        fields = ['uploaded_file', 'file_description']

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3}),
        }

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['type', 'description', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class YapilacakForm(forms.ModelForm):
    class Meta:
        model = Yapilacak
        fields = ['baslik', 'aciklama', 'son_tarih', 'tamamlandi']
        widgets = {
            'son_tarih': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'aciklama': forms.Textarea(attrs={'rows': 3}),
        }

class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ExpenseItemForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['description', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'description', 'date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CustomerQueryForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ara...'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

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
