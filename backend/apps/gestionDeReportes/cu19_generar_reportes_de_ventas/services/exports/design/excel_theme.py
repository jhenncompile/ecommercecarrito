from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class ExcelTheme:
    """
    Inyecta estilos corporativos limpios a hojas de Excel crudas de openpyxl.
    """

    @classmethod
    def apply_standard_format(cls, worksheet):
        """
        Aplica: 
        1. Cabeceras con fondo oscuro y texto blanco.
        2. Auto-ajuste inteligente de columnas.
        3. Alineamiento centrado.
        """
        # 1. Estilos para cabeceras
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2C3E50", end_color="2C3E50", fill_type="solid")
        
        # Borde delgado para celdas
        thin_border = Border(
            left=Side(style='thin', color='BDC3C7'),
            right=Side(style='thin', color='BDC3C7'),
            top=Side(style='thin', color='BDC3C7'),
            bottom=Side(style='thin', color='BDC3C7')
        )

        # Aplicar estilo a cabeceras (Fila 1)
        for cell in worksheet[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            cell.border = thin_border

        # 2. Ajustar ancho de columnas inteligentemente
        for col in worksheet.columns:
            max_length = 0
            column_letter = col[0].column_letter
            
            for cell in col:
                # Aplicar bordes al resto de celdas
                if cell.row > 1:
                    cell.border = thin_border
                    
                try:
                    if cell.value:
                        lines = str(cell.value).split('\n')
                        for line in lines:
                            if len(line) > max_length:
                                max_length = len(line)
                except:
                    pass
                    
            # Formula para autoajustar con límite máximo de 60
            adjusted_width = min((max_length + 2) * 1.2, 60)
            worksheet.column_dimensions[column_letter].width = adjusted_width
