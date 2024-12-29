import django_tables2 as tables
from django.utils.html import format_html
from .models import Customer

class CustomerTable(tables.Table):
    actions = tables.TemplateColumn(
        template_code='''
            <a href="{% url 'musteri:customer_detail' record.id %}" class="btn btn-info btn-sm">
                <i class="fas fa-eye"></i>
            </a>
            <a href="{% url 'musteri:customer_edit' record.id %}" class="btn btn-primary btn-sm">
                <i class="fas fa-edit"></i>
            </a>
        ''',
        orderable=False,
        verbose_name='Actions'
    )
    
    full_name = tables.Column(empty_values=(), order_by=('first_name', 'last_name'))
    status_display = tables.Column(empty_values=(), verbose_name='Status')
    
    def render_full_name(self, record):
        return f'{record.first_name} {record.last_name}'
    
    def render_status_display(self, record):
        status_colors = {
            'basvuru_yapildi': 'warning',
            'dosyalar_verildi': 'info',
            'ptt_bekleniyor': 'primary',
            'kart_alindi': 'success',
            'tamamlandi': 'secondary'
        }
        color = status_colors.get(record.status, 'secondary')
        status_text = dict(Customer.STATUS_CHOICES).get(record.status, record.status)
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            status_text
        )

    class Meta:
        model = Customer
        template_name = 'django_tables2/bootstrap5.html'
        fields = ('id', 'full_name', 'phone_number', 'nationality', 'passport_number', 
                 'residence_type', 'residence_permit_start_date', 'residence_permit_end_date',
                 'status_display', 'actions')
        attrs = {
            'class': 'table table-striped table-hover',
            'thead': {
                'class': 'table-dark'
            }
        }
