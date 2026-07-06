from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryZone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zone_name', models.CharField(max_length=120, verbose_name='Nombre de la Zona')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio de Envío')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
            ],
            options={
                'verbose_name': 'Zona de Delivery',
                'verbose_name_plural': 'Zonas de Delivery',
                'db_table': 'app_negocio_delivery_zone',
                'ordering': ['zone_name'],
                'constraints': [models.UniqueConstraint(fields=('zone_name',), name='unique_delivery_zone_por_tenant')],
            },
        ),
    ]
