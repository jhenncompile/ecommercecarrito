import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import pandas as pd

class BaseBuilder:
    def __init__(self, metadata: dict):
        self.metadata = metadata
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#2980b9'),
            spaceAfter=12
        )
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20
        )

    def build_pdf(self) -> HttpResponse:
        raise NotImplementedError("build_pdf no implementado")

    def build_excel(self) -> HttpResponse:
        raise NotImplementedError("build_excel no implementado")

    def _create_http_response(self, content: bytes, filename: str, content_type: str) -> HttpResponse:
        response = HttpResponse(content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    def _create_pdf_response(self, buffer: io.BytesIO, filename: str) -> HttpResponse:
        buffer.seek(0)
        return self._create_http_response(buffer.read(), filename, 'application/pdf')

    def _create_excel_response(self, buffer: io.BytesIO, filename: str) -> HttpResponse:
        buffer.seek(0)
        return self._create_http_response(
            buffer.read(), 
            filename, 
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
