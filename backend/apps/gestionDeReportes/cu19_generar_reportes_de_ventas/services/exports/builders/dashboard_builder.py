import io
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, KeepTogether
from reportlab.lib.pagesizes import landscape, letter
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.base_builder import BaseBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.theme import PDFTheme
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.charts import ChartRenderer
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.tables import TableDesigner
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.excel_theme import ExcelTheme

class DashboardBuilder(BaseBuilder):
    def build_pdf(self):
        blocks = self.metadata.get('blocks', [])
        title = self.metadata.get('title', 'Dashboard Dinámico')
        
        if not blocks:
            raise ValueError("No hay bloques en el dashboard para exportar.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        elements = []
        theme_styles = PDFTheme.get_styles()

        # Portada
        elements.append(Paragraph(title, theme_styles['CustomTitle']))
        elements.append(Paragraph(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", theme_styles['CustomSubtitle']))
        elements.append(Spacer(1, 30))

        for idx, block in enumerate(blocks):
            block_data = block.get('data', [])
            block_type = block.get('type')
            block_title = block.get('title', f'Bloque {idx+1}')

            if not block_data:
                continue

            block_header = []
            block_header.append(Paragraph(f"{idx + 1}. {block_title}", theme_styles['WidgetTitle']))
            
            if block_type == 'kpi':
                total = sum(float(d.get('resultado', 0)) for d in block_data)
                val_str = f"{total:,.0f}" if total % 1 == 0 else f"{total:,.2f}"
                block_header.append(Paragraph(val_str, theme_styles['KPIValue']))
                block_header.append(Spacer(1, 15))
                elements.append(KeepTogether(block_header))
            
            elif block_type in ['bar', 'line', 'pie', 'doughnut', 'horizontal', 'area', 'waterfall', 'funnel', 'stacked', 'sparkline', 'radar', 'heatmap', 'cohort']:
                labels = [str(d.get('grupo', d.get('label', 'General'))) for d in block_data]
                values = [float(d.get('resultado', d.get('value', 0))) for d in block_data]
                
                if block_type == 'bar':
                    img_buffer = ChartRenderer.draw_bar(labels, values)
                elif block_type == 'line':
                    img_buffer = ChartRenderer.draw_line(labels, values)
                elif block_type in ['pie', 'doughnut']:
                    img_buffer = ChartRenderer.draw_donut(labels, values)
                elif block_type == 'horizontal':
                    img_buffer = ChartRenderer.draw_horizontal(labels, values)
                elif block_type == 'area':
                    img_buffer = ChartRenderer.draw_area(labels, values)
                elif block_type == 'waterfall':
                    img_buffer = ChartRenderer.draw_waterfall(labels, values)
                elif block_type == 'funnel':
                    img_buffer = ChartRenderer.draw_funnel(labels, values)
                elif block_type == 'sparkline':
                    img_buffer = ChartRenderer.draw_sparkline(values)
                elif block_type == 'radar':
                    img_buffer = ChartRenderer.draw_radar(labels, values)
                elif block_type == 'stacked':
                    s1 = [float(d.get('segment1', 0)) for d in block_data]
                    s2 = [float(d.get('segment2', 0)) for d in block_data]
                    s3 = [float(d.get('segment3', 0)) for d in block_data]
                    img_buffer = ChartRenderer.draw_stacked(labels, s1, s2, s3)
                elif block_type == 'cohort':
                    cohorts = [str(d.get('cohort', d.get('label', 'C'))) for d in block_data]
                    matrix = [d.get('data', []) for d in block_data]
                    img_buffer = ChartRenderer.draw_cohort(cohorts, matrix)
                elif block_type == 'heatmap':
                    if isinstance(block_data, dict) and 'matrix' in block_data:
                        x_labels = block_data.get('times', [])
                        y_labels = block_data.get('days', [])
                        flat = block_data.get('matrix', [])
                    else:
                        x_labels = block_data[0].get('times', []) if isinstance(block_data, list) and block_data else []
                        y_labels = block_data[0].get('days', []) if isinstance(block_data, list) and block_data else []
                        flat = block_data[0].get('matrix', []) if isinstance(block_data, list) and block_data else []
                    
                    if x_labels and y_labels:
                        mat = []
                        for y in y_labels:
                            row = []
                            for x in x_labels:
                                cell = next((m for m in flat if m.get('day') == y and m.get('time') == x), None)
                                row.append(float(cell.get('value', 0)) if cell else 0)
                            mat.append(row)
                        img_buffer = ChartRenderer.draw_heatmap(x_labels, y_labels, mat)
                    else:
                        img_buffer = ChartRenderer.draw_bar(labels, values) # fallback
                else:
                    img_buffer = ChartRenderer.draw_bar(labels, values)
                
                img = Image(img_buffer, width=450, height=250)
                block_header.append(img)
                block_header.append(Spacer(1, 15))
                elements.append(KeepTogether(block_header))

                # Agregar tabla resumen debajo, dejando que fluya si es larga
                t = TableDesigner.create_data_table(block_data, block_type, block.get('config', {}))
                if t:
                    elements.append(t)
                elements.append(Spacer(1, 20))
                elements.append(PageBreak()) # Gráfico + Tabla ocupan su propia página
            
            elif block_type == 'table':
                elements.append(KeepTogether(block_header))
                t = TableDesigner.create_data_table(block_data, 'table', block.get('config', {}))
                if t:
                    elements.append(t)
                elements.append(Spacer(1, 20))
                elements.append(PageBreak())

        doc.build(elements)
        return self._create_pdf_response(buffer, f"dashboard_{int(datetime.now().timestamp())}.pdf")

    def build_excel(self):
        blocks = self.metadata.get('blocks', [])
        title = self.metadata.get('title', 'Dashboard')
        
        if not blocks:
            raise ValueError("No hay bloques para exportar a Excel.")

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            for idx, block in enumerate(blocks):
                block_data = block.get('data', [])
                if not block_data:
                    continue
                
                sheet_name = f"{idx+1}_{block.get('title', 'Bloque')[:25]}".replace('/', '_').replace('\\', '_')
                
                if block.get('type') == 'kpi':
                    total = sum(float(d.get('resultado', 0)) for d in block_data)
                    df = pd.DataFrame([{"Métrica": block.get('title'), "Valor Total": total}])
                elif block.get('type') == 'table':
                    selected_cols = block.get('config', {}).get('select', list(block_data[0].keys()))
                    formatted_data = []
                    for row in block_data:
                        formatted_data.append({c.replace('_', ' ').title(): row.get(c) for c in selected_cols})
                    df = pd.DataFrame(formatted_data)
                else:
                    df = pd.DataFrame([{"Grupo / Eje X": d.get('grupo', 'General'), "Valor / Eje Y": float(d.get('resultado', 0))} for d in block_data])
                    
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                
                # Usar Design Engine para formatear
                worksheet = writer.sheets[sheet_name]
                ExcelTheme.apply_standard_format(worksheet)
                
        return self._create_excel_response(buffer, f"dashboard_{int(datetime.now().timestamp())}.xlsx")
