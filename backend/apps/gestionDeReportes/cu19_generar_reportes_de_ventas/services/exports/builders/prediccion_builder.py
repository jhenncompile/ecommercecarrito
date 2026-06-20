import io
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, KeepTogether, PageBreak
from reportlab.lib.pagesizes import landscape, letter
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.base_builder import BaseBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.theme import PDFTheme
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.charts import ChartRenderer
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.tables import TableDesigner
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.excel_theme import ExcelTheme

class PrediccionBuilder(BaseBuilder):
    def build_pdf(self):
        title = self.metadata.get('title', 'Reporte de Predicciones')
        data = self.metadata.get('data', {})
        
        historico = data.get('historico', [])
        prediccion = data.get('predicciones', [])
        
        if not historico and not prediccion:
            raise ValueError("No hay datos de predicción para exportar")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        theme_styles = PDFTheme.get_styles()

        elements.append(Paragraph(title, theme_styles['CustomTitle']))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", theme_styles['CustomSubtitle']))
        elements.append(Spacer(1, 20))

        # 1. Dibujar el Gráfico
        # Preparar data para ChartRenderer
        all_labels = sorted(list(set(
            [p.get('periodo') for p in historico] + 
            [p.get('periodo') for p in prediccion]
        )))
        
        # Conectar la línea predictiva con el último dato histórico (igual que en frontend)
        if historico and prediccion:
            last_h = historico[-1].copy()
            last_h['cantidad_estimada'] = last_h.get('cantidad', 0)
            last_h['ic_inferior'] = last_h.get('cantidad', 0)
            last_h['ic_superior'] = last_h.get('cantidad', 0)
            prediccion_extended = [last_h] + prediccion
        else:
            prediccion_extended = prediccion

        hist_data = []
        pred_data = []
        lower_bound = []
        upper_bound = []
        
        for label in all_labels:
            h = next((x for x in historico if x.get('periodo') == label), None)
            p = next((x for x in prediccion_extended if x.get('periodo') == label), None)
            
            hist_data.append(h.get('cantidad') if h else None)
            pred_data.append(p.get('cantidad_estimada') if p else None)
            lower_bound.append(p.get('ic_inferior') if p else None)
            upper_bound.append(p.get('ic_superior') if p else None)

        chart_elements = []
        chart_elements.append(Paragraph("Gráfico de Predicción", theme_styles['WidgetTitle']))
        img_buffer = ChartRenderer.draw_prediction(all_labels, hist_data, pred_data, lower_bound, upper_bound)
        img = Image(img_buffer, width=450, height=250)
        chart_elements.append(img)
        chart_elements.append(Spacer(1, 20))
        
        elements.append(KeepTogether(chart_elements))
        elements.append(PageBreak()) # Separamos gráfico de la tabla

        # 2. Dibujar la Tabla
        elements.append(Paragraph("Datos Detallados", theme_styles['WidgetTitle']))
        
        # Formatear para tabla
        table_raw_data = []
        for p in prediccion:
            table_raw_data.append({
                'Período': p.get('periodo'),
                'Tipo': 'Predicción',
                'Valor Estimado': round(p.get('valor_predicho', p.get('cantidad_estimada', 0)), 2),
                'Límite Inferior': round(p.get('ic_inferior', 0), 2) if p.get('ic_inferior') else '—',
                'Límite Superior': round(p.get('ic_superior', 0), 2) if p.get('ic_superior') else '—'
            })
            
        t = TableDesigner.create_data_table(table_raw_data, 'table', {'select': ['Período', 'Tipo', 'Valor Estimado', 'Límite Inferior', 'Límite Superior']})
        if t:
            elements.append(t)

        doc.build(elements)
        return self._create_pdf_response(buffer, f"prediccion_{int(datetime.now().timestamp())}.pdf")

    def build_excel(self):
        title = self.metadata.get('title', 'Predicciones')
        data = self.metadata.get('data', {})
        prediccion = data.get('predicciones', [])
        
        if not prediccion:
            raise ValueError("No hay predicciones para exportar a Excel.")

        wsData = []
        for p in prediccion:
            wsData.append({
                'Período': p.get('periodo'),
                'Tipo': 'Predicción',
                'Valor Estimado': round(p.get('valor_predicho', p.get('cantidad_estimada', 0)), 2),
                'Límite Inferior': round(p.get('ic_inferior', 0), 2) if p.get('ic_inferior') else '',
                'Límite Superior': round(p.get('ic_superior', 0), 2) if p.get('ic_superior') else ''
            })

        df = pd.DataFrame(wsData)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            sheet_name = 'Predicciones'
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            # Usar Design Engine para formatear
            worksheet = writer.sheets[sheet_name]
            ExcelTheme.apply_standard_format(worksheet)
                
        return self._create_excel_response(buffer, f"prediccion_{int(datetime.now().timestamp())}.xlsx")
