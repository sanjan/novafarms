# Generated by Django 4.1.6 on 2023-09-05 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0045_rename_pallet_name_pallet_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='topinsert',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='lid_images'),
        ),
    ]
