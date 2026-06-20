from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile


def generar_excel_prediccion(datos):
    sheets = [
        ('Prediccion', _rows_prediccion(datos)),
        ('Historico', _rows_historico(datos)),
        ('Metricas', _rows_metricas(datos)),
    ]

    buffer = BytesIO()
    with ZipFile(buffer, 'w', ZIP_DEFLATED) as xlsx:
        xlsx.writestr('[Content_Types].xml', _content_types(len(sheets)))
        xlsx.writestr('_rels/.rels', _root_rels())
        xlsx.writestr('xl/workbook.xml', _workbook_xml(sheets))
        xlsx.writestr('xl/_rels/workbook.xml.rels', _workbook_rels(len(sheets)))
        for idx, (_, rows) in enumerate(sheets, start=1):
            xlsx.writestr(f'xl/worksheets/sheet{idx}.xml', _sheet_xml(rows))

    buffer.seek(0)
    return buffer


def _rows_prediccion(datos):
    rows = [[
        'Periodo',
        'Cantidad estimada',
        'Cantidad redondeada',
        'Precio actual',
        'Monto referencial',
        'IC inferior',
        'IC superior',
        'Confianza',
    ]]
    for pred in datos.get('predicciones', []):
        rows.append([
            pred.get('periodo', ''),
            pred.get('cantidad_estimada', ''),
            pred.get('cantidad_estimada_redondeada', ''),
            pred.get('precio_actual', ''),
            pred.get('monto_estimado_referencial', ''),
            pred.get('ic_inferior', ''),
            pred.get('ic_superior', ''),
            pred.get('confianza', ''),
        ])
    return rows


def _rows_historico(datos):
    rows = [['Periodo', 'Cantidad']]
    for punto in datos.get('historico', []):
        rows.append([punto.get('periodo', ''), punto.get('cantidad', '')])
    return rows


def _rows_metricas(datos):
    rows = [['Métrica', 'Valor']]
    for key, value in datos.get('metricas', {}).items():
        rows.append([key.replace('_', ' ').title(), value])
    rows.append(['Disclaimer', datos.get('disclaimer', '')])
    return rows


def _sheet_xml(rows):
    row_xml = []
    for r_idx, row in enumerate(rows, start=1):
        cells = []
        for c_idx, value in enumerate(row, start=1):
            ref = f'{_col_name(c_idx)}{r_idx}'
            cells.append(
                f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            )
        row_xml.append(f'<row r="{r_idx}">{"".join(cells)}</row>')

    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(row_xml)}</sheetData>'
        '</worksheet>'
    )


def _workbook_xml(sheets):
    sheet_xml = ''.join(
        f'<sheet name="{escape(name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        for idx, (name, _) in enumerate(sheets, start=1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        f'<sheets>{sheet_xml}</sheets>'
        '</workbook>'
    )


def _workbook_rels(sheet_count):
    rels = ''.join(
        f'<Relationship Id="rId{idx}" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        f'Target="worksheets/sheet{idx}.xml"/>'
        for idx in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'{rels}</Relationships>'
    )


def _root_rels():
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '</Relationships>'
    )


def _content_types(sheet_count):
    sheets = ''.join(
        '<Override '
        f'PartName="/xl/worksheets/sheet{idx}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        for idx in range(1, sheet_count + 1)
    )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        f'{sheets}</Types>'
    )


def _col_name(index):
    name = ''
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name
