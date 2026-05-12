from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from .tenant import Client
from .rol import Rol

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    username = None
    email = models.EmailField('email address', unique=True)
    
    tenant = models.ForeignKey(
        Client, 
        on_delete=models.CASCADE, 
        related_name='usuarios',
        null=True, 
        blank=True
    )
    
    roles = models.ManyToManyField(
        Rol,
        related_name='usuarios',
        blank=True,
        verbose_name='Roles'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    # --- Métodos extra requeridos para la gestión ---

    def status(self):
        """Retorna True si está activo, False si está desactivado"""
        return self.is_active

    def activate(self):
        """Activa el usuario"""
        self.is_active = True
        self.save(update_fields=['is_active'])

    def disable(self):
        """Desactiva el usuario"""
        self.is_active = False
        self.save(update_fields=['is_active'])

    @classmethod
    def mod(cls, id, **datos):
        """Modifica datos de un usuario identificándolo por id"""
        usuario = cls.objects.get(id=id)
        for key, value in datos.items():
            setattr(usuario, key, value)
        if 'password' in datos:
            usuario.set_password(datos['password'])
        usuario.save()
        return usuario