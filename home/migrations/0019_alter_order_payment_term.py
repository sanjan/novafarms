# Generated by Django 4.1.5 on 2023-01-12 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0018_alter_orderitem_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_term',
            field=models.CharField(choices=[('Immediate', 'Immediate'), ('30 Days', '30 Days')], max_length=20),
        ),
    ]
