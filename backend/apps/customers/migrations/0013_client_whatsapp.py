from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0012_client_logistica'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='whatsapp',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Número de WhatsApp de la Tienda'),
        ),
    ]
