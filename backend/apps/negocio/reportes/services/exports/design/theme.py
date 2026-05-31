from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class PDFTheme:
    """
    Define los colores corporativos, tipografías y estilos base
    para mantener consistencia visual en todos los PDFs.
    """
    
    # Paleta de Colores
    COLOR_PRIMARY = colors.HexColor('#2c3e50')    # Azul oscuro (títulos, fondos de cabecera)
    COLOR_SECONDARY = colors.HexColor('#3498db')  # Azul claro (acentos)
    COLOR_SUCCESS = colors.HexColor('#27ae60')    # Verde esmeralda (KPIs)
    COLOR_DANGER = colors.HexColor('#e74c3c')     # Rojo (alertas)
    COLOR_MUTED = colors.HexColor('#7f8c8d')      # Gris (subtítulos)
    COLOR_BACKGROUND = colors.HexColor('#f8fafc') # Gris muy claro (filas alternas)
    COLOR_BORDER = colors.HexColor('#bdc3c7')     # Gris medio (bordes)
    
    @classmethod
    def get_styles(cls):
        styles = getSampleStyleSheet()
        
        # Título principal
        styles.add(ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=cls.COLOR_PRIMARY,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo (Fechas, filtros)
        styles.add(ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=cls.COLOR_MUTED,
            spaceAfter=20,
            fontName='Helvetica'
        ))
        
        # Título de Widgets/Bloques
        styles.add(ParagraphStyle(
            'WidgetTitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=cls.COLOR_PRIMARY,
            spaceAfter=10,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))

        # KPI valor en grande
        styles.add(ParagraphStyle(
            'KPIValue',
            parent=styles['Normal'],
            fontSize=28,
            textColor=cls.COLOR_SUCCESS,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))

        return styles
