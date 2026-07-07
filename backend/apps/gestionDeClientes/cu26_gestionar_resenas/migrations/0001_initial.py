import django.core.validators
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
            name='Resena',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calificacion', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Calificación (1 a 5 estrellas)')),
                ('comentario', models.TextField(blank=True, default='', verbose_name='Comentario')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de la Reseña')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resenas', to='customers.cliente', verbose_name='Cliente')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resenas', to='cu7_gestionar_productos.producto', verbose_name='Producto')),
            ],
            options={
                'verbose_name': 'Reseña',
                'verbose_name_plural': 'Reseñas',
                'db_table': 'app_negocio_resena',
                'ordering': ['-created_at'],
                'constraints': [models.UniqueConstraint(fields=('cliente', 'producto'), name='unique_resena_por_cliente_producto')],
            },
        ),
    ]
