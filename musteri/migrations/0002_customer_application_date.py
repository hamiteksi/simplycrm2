# Generated by Django 4.2.7 on 2025-01-02 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musteri', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='application_date',
            field=models.DateField(blank=True, default=None, help_text='Müşterinin başvuru tarihi', null=True, verbose_name='Başvuru Tarihi'),
        ),
    ]
