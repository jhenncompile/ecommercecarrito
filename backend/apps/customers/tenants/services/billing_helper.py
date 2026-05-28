from datetime import date, datetime
import calendar

class BillingDateHelper:
    """
    Servicio utilitario para manejar lógicas complejas de fechas de facturación.
    Especialmente diseñado para lidiar con años bisiestos y meses de 28, 29, 30 y 31 días.
    """
    
    @staticmethod
    def calcular_fechas_mensuales(fecha_inicio=None):
        """
        Calcula la fecha de inicio y la fecha de fin (1 mes exacto) desde la fecha_inicio.
        Aplica correcciones para fin de mes. Ejemplo:
        Si inicia el 31 de Enero, finaliza el 28 de Febrero (o 29 si es bisiesto).
        """
        if not fecha_inicio:
            fecha_inicio = date.today()
            
        mes = fecha_inicio.month
        anio = fecha_inicio.year
        dia = fecha_inicio.day
        
        # Calcular el mes siguiente
        siguiente_mes = mes + 1 if mes < 12 else 1
        siguiente_anio = anio if mes < 12 else anio + 1
        
        # Obtener el último día posible del siguiente mes
        _, ultimo_dia_siguiente_mes = calendar.monthrange(siguiente_anio, siguiente_mes)
        
        # El día de cobro será el mínimo entre el día en que contrató y el último día del mes siguiente
        dia_siguiente = min(dia, ultimo_dia_siguiente_mes)
        
        fecha_fin = date(siguiente_anio, siguiente_mes, dia_siguiente)
        
        return fecha_inicio, fecha_fin
