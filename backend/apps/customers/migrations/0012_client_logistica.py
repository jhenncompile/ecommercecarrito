from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0011_client_limite_alcanzado_fecha_plan_ventas_max_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='ciudad',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Ciudad de la Tienda'),
        ),
        migrations.AddField(
            model_name='client',
            name='enable_local_delivery',
            field=models.BooleanField(default=False, verbose_name='Habilitar Delivery Local'),
        ),
        migrations.AddField(
            model_name='client',
            name='enable_national_shipping',
            field=models.BooleanField(default=True, verbose_name='Habilitar Envío Nacional (Encomienda)'),
        ),
    ]
