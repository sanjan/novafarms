# Generated by Django 4.1.5 on 2023-02-06 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_alter_batch_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]
