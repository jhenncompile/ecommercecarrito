from .registry import ReportRegistry
# Importamos los modulos para que se registren los decoradores
import apps.negocio.reportes.services.estaticos
import apps.negocio.reportes.services.builders

class ReportService:
    @staticmethod
    def generar_estatico(tipo):
        """
        Obtiene y ejecuta el reporte estático desde el registro.
        """
        funcion_reporte = ReportRegistry.get_estatico(tipo)
        return funcion_reporte()

    @staticmethod
    def ejecutar_dinamico(config):
        """
        Obtiene el builder dinámico y ejecuta la consulta armada.
        """
        modelo_str = config.get('modelo', 'pedidos')
        BuilderClass = ReportRegistry.get_dinamico_builder(modelo_str)
        builder = BuilderClass(config)
        return builder.build()

