# Generated by Django 4.1.6 on 2023-02-12 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_customer_customer_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pallet',
            name='dimensions',
        ),
        migrations.AddField(
            model_name='pallet',
            name='height',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pallet',
            name='width',
            field=models.IntegerField(default=0),
        ),
    ]
