# Generated by Django 4.2.17 on 2025-01-31 00:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('producto', '0005_notificacion_cantidad'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='numero_serie',
            field=models.CharField(default='', editable=False, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='notificacion',
            name='cantidad',
            field=models.PositiveIntegerField(),
        ),
    ]
