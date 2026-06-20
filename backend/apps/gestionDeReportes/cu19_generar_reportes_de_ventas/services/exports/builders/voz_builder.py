import io
import pandas as pd
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, KeepTogether, PageBreak
)
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors

from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.builders.base_builder import BaseBuilder
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.theme import PDFTheme
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.tables import TableDesigner
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.excel_theme import ExcelTheme
from apps.gestionDeReportes.cu19_generar_reportes_de_ventas.services.exports.design.charts import ChartRenderer


class VozBuilder(BaseBuilder):
    """
    Builder para exportar resultados de consultas generadas por el Asistente de Voz IA.
    Recibe en metadata:
        - 'transcripcion': texto de lo que el usuario dijo (usado como título)
        - 'data': lista de dicts con los resultados de la query SQL
    """

    def _get_data_and_title(self):
        transcripcion = self.metadata.get('transcripcion', 'Consulta por Voz')
        data = self.metadata.get('data', [])
        title = f'Resultado: "{transcripcion}"'
        return data, title, transcripcion

    def build_pdf(self):
        data, title, transcripcion = self._get_data_and_title()

        if not data:
            raise ValueError("No hay datos para exportar en el reporte de voz.")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(letter),
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=18
        )
        elements = []
        theme_styles = PDFTheme.get_styles()

        # ── Encabezado ──────────────────────────────────────────────
        elements.append(Paragraph("Asistente de Voz IA — Reporte Generado", theme_styles['CustomTitle']))
        elements.append(Paragraph(
            f'Consulta: "{transcripcion}"',
            theme_styles['CustomSubtitle']
        ))
        elements.append(Paragraph(
            f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Registros: {len(data)}",
            theme_styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 16))

        # ── Gráfico automático (si hay datos numéricos) ─────────────
        try:
            keys = list(data[0].keys())
            label_cands = ['nombre', 'producto', 'categoria', 'mes', 'dia', 'estado', 'periodo', 'descripcion']
            label_key = next((k for k in keys if any(c in k.lower() for c in label_cands)), keys[0])

            val_cands = ['total', 'cantidad', 'precio', 'monto', 'stock', 'ventas', 'rentabilidad', 'ganancia']
            val_key = next(
                (k for k in keys if any(c in k.lower() for c in val_cands) and k != label_key),
                keys[1] if len(keys) > 1 else None
            )

            if val_key:
                labels = [str(row.get(label_key, 'N/A'))[:20] for row in data[:20]]  # máx 20 barras
                values = []
                for row in data[:20]:
                    try:
                        values.append(float(row.get(val_key, 0) or 0))
                    except (ValueError, TypeError):
                        values.append(0)

                if any(v > 0 for v in values):
                    chart_group = []
                    chart_group.append(Paragraph(
                        f"Gráfico: {str(val_key).replace('_', ' ').title()} por {str(label_key).replace('_', ' ').title()}",
                        theme_styles.get('WidgetTitle', theme_styles['Normal'])
                    ))
                    img_buffer = ChartRenderer.draw_bar(labels, values)
                    img = Image(img_buffer, width=500, height=260)
                    chart_group.append(img)
                    chart_group.append(Spacer(1, 12))
                    elements.append(KeepTogether(chart_group))
                    elements.append(PageBreak())
        except Exception:
            pass  # Si falla el gráfico, continuamos sin él

        # ── Tabla de datos ──────────────────────────────────────────
        t = TableDesigner.create_data_table(data, 'table', {'select': list(data[0].keys())})
        if t:
            elements.append(t)

        doc.build(elements)
        return self._create_pdf_response(buffer, f"reporte_voz_{int(datetime.now().timestamp())}.pdf")

    def build_excel(self):
        data, title, transcripcion = self._get_data_and_title()

        if not data:
            raise ValueError("No hay datos para exportar en el reporte de voz.")

        df = pd.DataFrame(data)

        buffer = io.BytesIO()
        sheet_name = f"Consulta Voz"
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            worksheet = writer.sheets[sheet_name]
            ExcelTheme.apply_standard_format(worksheet)

        return self._create_excel_response(buffer, f"reporte_voz_{int(datetime.now().timestamp())}.xlsx")
