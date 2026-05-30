from django.db import models
import os

def release_upload_path(instance, filename):
    # Esto guardarÃ¡ el archivo en: public/media/app/<cliente|vendedor>/version/1.0.0/release.apk
    return f"app/{instance.app_type}/version/{instance.version}/release.apk"

class MobileRelease(models.Model):
    APP_CHOICES = [
        ('cliente', 'App Cliente'),
        ('vendedor', 'App Vendedor'),
    ]

    app_type = models.CharField('Tipo de App', max_length=20, choices=APP_CHOICES)
    version = models.CharField('VersiÃ³n', max_length=20)
    file = models.FileField('Archivo APK', upload_to=release_upload_path)
    is_latest = models.BooleanField('Es la Ãºltima versiÃ³n', default=False)
    created_at = models.DateTimeField('Fecha de Subida', auto_now_add=True)

    class Meta:
        db_table = 'mobile_release'
        verbose_name = 'Release MÃ³vil'
        verbose_name_plural = 'Releases MÃ³viles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_app_type_display()} - v{self.version}"

    def save(self, *args, **kwargs):
        # Si se marca como la Ãºltima versiÃ³n, desactivar is_latest en las demÃ¡s
        if self.is_latest:
            MobileRelease.objects.filter(app_type=self.app_type, is_latest=True).update(is_latest=False)
        super().save(*args, **kwargs)
