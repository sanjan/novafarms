# Generated by Django 4.1.5 on 2023-01-09 07:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_rename_addressline_1_beekeeper_address_line_1_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_weight', models.PositiveIntegerField()),
                ('ibc_weight', models.PositiveIntegerField()),
                ('net_weight', models.PositiveIntegerField()),
                ('honey_levy', models.PositiveIntegerField()),
                ('total_price', models.PositiveBigIntegerField()),
                ('immediate_payment', models.BooleanField()),
                ('bee_keeper', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.beekeeper')),
            ],
        ),
    ]
