# Generated by Django 4.2.17 on 2025-01-06 19:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('producto', '0003_prestamo_notificacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bodega',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='prestamo',
            name='bodega',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prestamos', to='producto.bodega'),
        ),
        migrations.AddField(
            model_name='producto',
            name='bodega',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='producto', to='producto.bodega'),
        ),
    ]
