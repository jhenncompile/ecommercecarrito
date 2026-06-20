from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.base_builder import BaseBuilder

class FacturacionBuilder(BaseBuilder):
    def build_pdf(self):
        # ESQUELETO PREPARADO PARA IMPLEMENTACIÓN DE FACTURAS
        # Aquí se usaría ReportLab para pintar una factura real con su diseño de logo, etc.
        raise NotImplementedError("Constructor de Facturas PDF no implementado")

    def build_excel(self):
        raise NotImplementedError("Constructor de Facturas Excel no implementado")
