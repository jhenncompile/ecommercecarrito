from apps.gestionDeUsuarioySeguridad.cu6_gestionar_bitacora.services.bitacora_service import BitacoraService


class AuditoriaMixin:
    """
    Registra automÃ¡ticamente las acciones de CREAR, EDITAR y ELIMINAR en la BitÃ¡cora.
    Requiere que la vista hija defina el atributo 'modulo_auditoria'.
    """
    modulo_auditoria = None

    def perform_create(self, serializer):
        instancia = serializer.save()
        if self.modulo_auditoria:
            BitacoraService.registrar_accion(
                self.request.user, self.modulo_auditoria, "CREAR",
                request=self.request,
                metadatos={'id': instancia.id}
            )

    def perform_update(self, serializer):
        instancia = serializer.save()
        if self.modulo_auditoria:
            BitacoraService.registrar_accion(
                self.request.user, self.modulo_auditoria, "EDITAR",
                request=self.request,
                metadatos={'id': instancia.id, 'cambios': serializer.initial_data}
            )

    def perform_destroy(self, instance):
        id_instancia = instance.id
        instance.delete()
        if self.modulo_auditoria:
            BitacoraService.registrar_accion(
                self.request.user, self.modulo_auditoria, "ELIMINAR",
                request=self.request,
                metadatos={'id': id_instancia}
            )
