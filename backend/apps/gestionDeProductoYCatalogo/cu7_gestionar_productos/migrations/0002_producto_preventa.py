from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cu7_gestionar_productos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='is_preorder',
            field=models.BooleanField(default=False, verbose_name='En Preventa'),
        ),
        migrations.AddField(
            model_name='producto',
            name='estimated_arrival_date',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha Estimada de Llegada'),
        ),
        migrations.AddField(
            model_name='producto',
            name='preorder_discount_percentage',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Descuento de Preventa (%)'),
        ),
    ]
