from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.dashboard_builder import DashboardBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.estatico_builder import EstaticoBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.facturacion_builder import FacturacionBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.voz_builder import VozBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.prediccion_builder import PrediccionBuilder

class ExportOrchestrator:
    @staticmethod
    def generate(export_type: str, fmt: str, metadata: dict):
        """
        Orquesta la generación de PDFs o Excels según el tipo.
        Devuelve un objeto HttpResponse listo para ser descargado.
        """
        BUILDERS = {
            'dashboard': DashboardBuilder,
            'dinamico': DashboardBuilder,
            'estatico': EstaticoBuilder,
            'facturacion': FacturacionBuilder,
            'voz': VozBuilder,
            'prediccion': PrediccionBuilder
        }

        builder_class = BUILDERS.get(export_type, EstaticoBuilder)
        builder = builder_class(metadata)

        if fmt == 'pdf':
            return builder.build_pdf()
        elif fmt == 'excel' or fmt == 'xlsx':
            return builder.build_excel()
        else:
            raise ValueError(f"Formato no soportado: {fmt}")
