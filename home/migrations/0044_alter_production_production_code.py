# Generated by Django 4.1.6 on 2023-09-03 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0043_production_produced_weight'),
    ]

    operations = [
        migrations.AlterField(
            model_name='production',
            name='production_code',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
