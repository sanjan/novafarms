# Generated by Django 4.1.5 on 2023-02-06 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_rename_date_batch_batch_date_batch_product_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batch',
            old_name='unit_weight_grams',
            new_name='unit_weight',
        ),
    ]
