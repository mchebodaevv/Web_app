# Generated by Django 5.1.5 on 2025-03-04 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory_devices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='responsible',
            name='status',
            field=models.CharField(choices=[('Выдано', 'Выдано'), ('Возвращено', 'Возвращено')], max_length=45, verbose_name='Статус'),
        ),
    ]
