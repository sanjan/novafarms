# Generated by Django 4.1.5 on 2023-02-04 16:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0023_orderitem_net_weight_orderitem_nv_ibc_batch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='batch',
            old_name='containers',
            new_name='source_containers',
        ),
        migrations.AddField(
            model_name='batch',
            name='bottle_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='brand',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='expiry_date',
            field=models.DateField(default=datetime.date(2023, 2, 14)),
        ),
        migrations.AddField(
            model_name='batch',
            name='max_possible',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='number_made',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='total_weight',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='batch',
            name='unit_weight',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
