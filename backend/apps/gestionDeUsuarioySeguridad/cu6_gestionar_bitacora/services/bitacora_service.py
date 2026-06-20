from ..models.bitacora import Bitacora

class BitacoraService:
    @staticmethod
    def _obtener_cliente_info(request):
        """Extrae IP y User-Agent del request de forma segura."""
        if not request:
            return "127.0.0.1", "CLI/System"
            
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
        browser = request.META.get('HTTP_USER_AGENT', 'Desconocido')
        return ip, browser

    @staticmethod
    def _filtrar_datos_sensibles(metadatos):
        """Elimina campos sensibles como passwords de los metadatos."""
        if not metadatos or not isinstance(metadatos, dict):
            return metadatos
            
        campos_sensibles = ['password', 'contraseña', 'token', 'refresh', 'secret']
        metadatos_limpios = metadatos.copy()
        
        for campo in list(metadatos_limpios.keys()):
            campo_lower = campo.lower()
            if any(sensible in campo_lower for sensible in campos_sensibles):
                metadatos_limpios[campo] = "********"
        
        return metadatos_limpios

    @classmethod
    def registrar(cls, user, modulo, accion, request=None, metadatos=None):
        """
        Método genérico para registrar en la bitácora.
        user: El objeto usuario que realiza la acción.
        modulo: Nombre del módulo (ej. 'Autenticación', 'Productos').
        accion: Tipo de acción (ej. 'LOGIN', 'CREAR').
        request: (Opcional) Objeto HttpRequest para capturar IP y Browser.
        metadatos: (Opcional) Diccionario con detalles adicionales.
        """
        if not user or user.is_anonymous:
            # En login fallido o similar, el usuario podría no estar autenticado
            # pero el requerimiento pide idUsuario (FK), así que ignoramos anónimos por ahora
            # o podríamos usar un usuario de sistema si fuera necesario.
            return None

        # Si el usuario proviene de ClienteTokenUser (PublicStorefront), ignorar auditoría
        # ya que la Bitácora requiere un objeto Usuario
        from apps.gestionDeUsuarioySeguridad.cu3_gestion_de_usuario.models.usuario import Usuario
        if not isinstance(user, Usuario):
            return None

        final_metadatos = metadatos or {}
        
        # Inyectar IP y Navegador si hay request
        ip, browser = cls._obtener_cliente_info(request)
        if ip:
            final_metadatos['ip'] = ip
        if browser:
            final_metadatos['browser'] = browser
            
        # Limpiar datos sensibles
        final_metadatos = cls._filtrar_datos_sensibles(final_metadatos)
        
        return Bitacora.objects.create(
            idUsuario=user,
            modulo=modulo,
            accion=accion,
            metadatos=final_metadatos
        )

    @classmethod
    def registrar_acceso(cls, request, user, accion):
        """Especializado para Login/Logout."""
        return cls.registrar(user, "Autenticación", accion, request=request)

    @classmethod
    def registrar_accion(cls, user, modulo, accion, metadatos=None, request=None):
        """Especializado para acciones de negocio."""
        return cls.registrar(user, modulo, accion, request=request, metadatos=metadatos)
