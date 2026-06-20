from reportlab.platypus import Table, TableStyle
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.theme import PDFTheme

class TableDesigner:
    """
    Motor de diseño para Tablas Analíticas en PDFs.
    """

    @classmethod
    def create_data_table(cls, data, block_type, config):
        """
        Toma una lista de diccionarios (datos crudos) y devuelve un Table de ReportLab
        con estilos corporativos.
        """
        if not data:
            return None

        if block_type == 'table':
            selected_cols = config.get('select', list(data[0].keys()))
            headers = [c.replace('_', ' ').title() for c in selected_cols]
            table_data = [headers]
            for row in data:
                table_data.append([str(row.get(c, '—')) for c in selected_cols])
        else:
            # Gráficos genéricos (leyenda debajo del gráfico)
            headers = ['Categoría', 'Valor']
            table_data = [headers]
            for row in data:
                # Tratar de formatear el valor numérico
                val = row.get('resultado', 0)
                try:
                    val_float = float(val)
                    val_str = f"{val_float:,.2f}"
                except (ValueError, TypeError):
                    val_str = str(val)
                table_data.append([str(row.get('grupo', 'General')), val_str])

        # Crear tabla y aplicar estilos
        t = Table(table_data)
        
        # Zebra Striping y estilo general
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), PDFTheme.COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), '#ffffff'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, PDFTheme.COLOR_BORDER),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]
        
        # Agregar Zebra Striping (Filas pares blancas, impares grises claro)
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), PDFTheme.COLOR_BACKGROUND))
            else:
                style.append(('BACKGROUND', (0, i), (-1, i), '#ffffff'))
                
        t.setStyle(TableStyle(style))
        return t
