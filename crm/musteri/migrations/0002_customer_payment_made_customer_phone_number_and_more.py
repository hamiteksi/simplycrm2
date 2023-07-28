# Generated by Django 4.1.7 on 2023-05-28 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musteri', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='payment_made',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='ptt_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='residence_permit_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='residence_permit_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]