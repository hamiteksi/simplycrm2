import django_tables2 as tables
from .models import Customer
from django.utils.html import format_html

class CustomerTable(tables.Table):
    actions = tables.Column(empty_values=(), orderable=False)
    full_name = tables.Column(accessor='get_full_name', verbose_name='Ad Soyad', order_by=('first_name', 'last_name'))
    status_display = tables.Column(accessor='get_status_display', verbose_name='Durum')
    
    class Meta:
        model = Customer
        template_name = "django_tables2/bootstrap4.html"
        fields = ('full_name', 'application_number', 'phone', 'residence_permit_start_date', 'residence_permit_end_date', 'status_display', 'actions')
        attrs = {
            'class': 'table table-hover',
            'thead': {
                'class': 'table-light'
            }
        }
        row_attrs = {
            'class': 'align-middle'
        }

    def render_actions(self, record):
        buttons = []
        
        # Detay butonu
        buttons.append(
            f'<a href="/customers/{record.id}/" class="btn btn-sm btn-outline-primary" title="Detay">'
            '<i class="fas fa-eye"></i>'
            '</a>'
        )
        
        # Düzenle butonu
        buttons.append(
            f'<a href="/customers/{record.id}/edit/" class="btn btn-sm btn-outline-warning" title="Düzenle">'
            '<i class="fas fa-edit"></i>'
            '</a>'
        )
        
        # WhatsApp butonu (telefon varsa)
        if record.phone:
            clean_phone = ''.join(filter(str.isdigit, record.phone))
            if clean_phone:
                buttons.append(
                    f'<a href="https://wa.me/{clean_phone}" target="_blank" '
                    'class="btn btn-sm btn-outline-success" title="WhatsApp">'
                    '<i class="fab fa-whatsapp"></i>'
                    '</a>'
                )
        
        return format_html(
            '<div class="btn-group">{}</div>',
            format_html(''.join(buttons))
        )

    def render_status_display(self, value):
        status_colors = {
            'Aktif': 'success',
            'Pasif': 'danger',
            'Beklemede': 'warning',
            'Tamamlandı': 'info'
        }
        color = status_colors.get(value, 'secondary')
        return format_html('<span class="badge bg-{}">{}</span>', color, value)

    def render_residence_permit_start_date(self, value):
        return value.strftime('%d.%m.%Y') if value else '-'

    def render_residence_permit_end_date(self, value):
        return value.strftime('%d.%m.%Y') if value else '-'
