# Generated for sales prediction cache

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_negocio', '0008_reporteconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrediccionCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario_id', models.IntegerField(blank=True, null=True)),
                ('usuario_email', models.EmailField(blank=True, default='', max_length=254)),
                ('configuracion', models.JSONField(verbose_name='Configuración')),
                ('resultado', models.JSONField(verbose_name='Resultado')),
                ('hash_config', models.CharField(db_index=True, max_length=64, unique=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_expiracion', models.DateTimeField(verbose_name='Expira en')),
                ('vigente', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Caché de Predicción',
                'verbose_name_plural': 'Cachés de Predicción',
                'db_table': 'app_negocio_prediccion_cache',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
