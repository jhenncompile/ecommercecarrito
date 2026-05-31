import io
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether, PageBreak
from reportlab.lib.pagesizes import landscape, letter
from apps.negocio.reportes.services.exports.builders.base_builder import BaseBuilder
from apps.negocio.reportes.services.exports.design.theme import PDFTheme
from apps.negocio.reportes.services.exports.design.tables import TableDesigner
from apps.negocio.reportes.services.exports.design.excel_theme import ExcelTheme
from apps.negocio.reportes.services.exports.design.charts import ChartRenderer

class EstaticoBuilder(BaseBuilder):
    def build_pdf(self):
        title = self.metadata.get('title', 'Reporte Estático')
        data = self.metadata.get('data', [])
        
        if not data:
            raise ValueError("No hay datos para exportar")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []
        theme_styles = PDFTheme.get_styles()

        elements.append(Paragraph(title, theme_styles['CustomTitle']))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", theme_styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))

        # Intentar dibujar un gráfico automático (como ReportChart en React)
        try:
            keys = list(data[0].keys())
            label_cands = ['mes', 'año', 'dia', 'nombre', 'categoria', 'estado', 'periodo']
            label_key = next((k for k in keys if k in label_cands), keys[0])
            
            val_cands = ['total_ventas', 'total', 'cantidad_pedidos', 'cantidad_productos', 'stock', 'conteo', 'precio']
            val_key = next((k for k in keys if k in val_cands), keys[1] if len(keys) > 1 else keys[0])

            labels = [str(row.get(label_key, 'N/A')) for row in data]
            values = []
            for row in data:
                try:
                    values.append(float(row.get(val_key, 0)))
                except (ValueError, TypeError):
                    values.append(0)
            
            # Solo si hay datos numéricos útiles
            if any(v > 0 for v in values):
                chart_elements = []
                chart_elements.append(Paragraph(f"Gráfico de {str(val_key).replace('_', ' ').title()}", theme_styles['WidgetTitle']))
                img_buffer = ChartRenderer.draw_bar(labels, values)
                img = Image(img_buffer, width=450, height=250)
                chart_elements.append(img)
                chart_elements.append(Spacer(1, 20))
                
                # Mantenemos el gráfico y su título juntos
                elements.append(KeepTogether(chart_elements))
                # Forzamos que la tabla empiece en una nueva página si el usuario quiere "cada hoja un gráfico"
                # o podemos dejar que fluya. Aquí ponemos PageBreak para separar gráfico de la tabla detallada.
                elements.append(PageBreak())
        except Exception as e:
            pass # Si falla el gráfico automático, simplemente no lo mostramos

        # Usar el TableDesigner
        # Emulamos un config type 'table' con la data cruda
        t = TableDesigner.create_data_table(data, 'table', {'select': list(data[0].keys())})
        if t:
            elements.append(t)
        doc.build(elements)
        
        return self._create_pdf_response(buffer, f"reporte_estatico_{int(datetime.now().timestamp())}.pdf")

    def build_excel(self):
        title = self.metadata.get('title', 'Reporte Estático')
        data = self.metadata.get('data', [])
        
        if not data:
            raise ValueError("No hay datos para exportar")

        df = pd.DataFrame(data)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            sheet_name = title[:31].replace('/', '_').replace('\\', '_')
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            # Usar Design Engine para formatear
            worksheet = writer.sheets[sheet_name]
            ExcelTheme.apply_standard_format(worksheet)
        
        return self._create_excel_response(buffer, f"reporte_{int(datetime.now().timestamp())}.xlsx")
