# Generated by Django 5.0.2 on 2024-03-21 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('musteri', '0026_alter_customer_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='application_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='first_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customer',
            name='last_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='customer',
            name='nationality',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='customer',
            name='residence_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
