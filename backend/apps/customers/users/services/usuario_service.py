from apps.core.services import BaseService
from apps.customers.users.models.usuario import Usuario

class UsuarioService(BaseService):
    def __init__(self):
        super().__init__(Usuario)

    def crear_usuario(self, datos_validados):
        """Crea usuario con contraseña segura."""
        password = datos_validados.pop('password', None)
        roles = datos_validados.pop('roles', [])
        user = Usuario(**datos_validados)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        if roles:
            user.roles.set(roles)
        return user

    def actualizar_usuario(self, instancia, datos_validados):
        """Actualiza usuario y gestiona password si viene en el request."""
        password = datos_validados.pop('password', None)
        roles = datos_validados.pop('roles', None)
        user = super().actualizar(instancia, datos_validados)
        if password:
            user.set_password(password)
            user.save()
        if roles is not None:
            user.roles.set(roles)
        return user

    def activar(self, usuario):
        usuario.is_active = True
        usuario.save()
        return usuario

    def desactivar(self, usuario):
        usuario.is_active = False
        usuario.save()
        return usuario