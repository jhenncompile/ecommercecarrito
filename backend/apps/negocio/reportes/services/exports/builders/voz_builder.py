from apps.negocio.reportes.services.exports.builders.base_builder import BaseBuilder

class VozBuilder(BaseBuilder):
    def build_pdf(self):
        # ESQUELETO PREPARADO PARA IMPLEMENTACIÓN DE REPORTE POR VOZ
        raise NotImplementedError("Constructor de Reportes de Voz PDF no implementado")

    def build_excel(self):
        raise NotImplementedError("Constructor de Reportes de Voz Excel no implementado")
