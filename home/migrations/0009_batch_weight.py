# Generated by Django 4.1.6 on 2023-02-13 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_remove_batch_production_production_production_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='weight',
            field=models.DecimalField(decimal_places=2, default=0.0, editable=False, max_digits=10),
        ),
    ]