import django_tables2 as tables
from .models import Customer

class CustomerTable(tables.Table):
    edit = tables.TemplateColumn(template_name='musteri/edit_column.html', orderable=False)
    detail = tables.TemplateColumn(template_name='musteri/detail_column.html', orderable=False)
    passport_number = tables.Column(default=" ", empty_values=[])
    application_number = tables.Column(default=" ", empty_values=[])
    identity_number = tables.Column(empty_values=[])  # We want to handle NaN values ourselves

    def render_identity_number(self, value):
        if value is None:
        # Eğer value None ise, boş bir string veya belirtmek istediğiniz bir metni döndürün
            return "Bilgi Yok"
        try:
            # Try to convert the value to float and then to int
            float_value = float(value)
            int_value = int(float_value)
            return str(int_value)
        except ValueError:
            # If value is not a float, just return it as is
            return value

    class Meta:
        model = Customer
        template_name = 'django_tables2/bootstrap.html'
        fields = ('id', 'first_name', 'last_name', 'application_number', 'nationality', 'passport_number', 'identity_number', 'residence_type', 'residence_permit_start_date', 'residence_permit_end_date')
        empty_text = ""



