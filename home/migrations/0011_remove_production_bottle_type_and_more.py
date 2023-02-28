# Generated by Django 4.1.6 on 2023-02-15 16:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_remove_honeystock_batch_batch_honey_stock'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='production',
            name='bottle_type',
        ),
        migrations.RemoveField(
            model_name='production',
            name='production',
        ),
        migrations.AddField(
            model_name='label',
            name='container_type',
            field=models.CharField(choices=[('Jar', 'Jar'), ('Squeeze Bottle', 'Squeeze Bottle'), ('Pail', 'Pail')], default='Squeeze Bottle', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lid',
            name='container_type',
            field=models.CharField(choices=[('Jar', 'Jar'), ('Squeeze Bottle', 'Squeeze Bottle'), ('Pail', 'Pail')], default='Squeeze Bottle', max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='production',
            name='batch',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='batch', to='home.batch'),
        ),
    ]