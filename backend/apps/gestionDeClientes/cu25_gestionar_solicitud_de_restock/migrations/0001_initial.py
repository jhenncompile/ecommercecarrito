import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
        ('cu7_gestionar_productos', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='RestockRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('notified', 'Notificado'), ('fulfilled', 'Atendido')], default='pending', max_length=20, verbose_name='Estado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Solicitud')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restock_requests', to='customers.cliente', verbose_name='Cliente')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restock_requests', to='cu7_gestionar_productos.producto', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Solicitud de Restock',
                'verbose_name_plural': 'Solicitudes de Restock',
                'db_table': 'app_negocio_restock_request',
                'ordering': ['-created_at'],
                'constraints': [models.UniqueConstraint(fields=('cliente', 'producto'), name='unique_restock_por_cliente_producto')],
            },
        ),
    ]
