# Generated by Django 4.2.3 on 2023-08-07 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_batch_honey_type_alter_batch_batch_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='tank_number',
            field=models.CharField(blank=True, max_length=3, null=True, unique=True),
        ),
    ]
