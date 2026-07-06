from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cu13_gestionar_estado_de_pedido', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='tipo_envio',
            field=models.CharField(blank=True, choices=[('LOCAL', 'Delivery Local'), ('ENCOMIENDA', 'Envío por Encomienda (Pago en Destino)')], max_length=20, null=True, verbose_name='Tipo de Envío'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='costo_envio',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Costo de Envío'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='ciudad_envio',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ciudad de Envío'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='zona_envio',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Zona de Delivery'),
        ),
    ]
