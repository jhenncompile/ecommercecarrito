from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, KeepTogether, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from django.db import connection
from apps.customers.models import Client
from django.utils.timezone import localtime

def generar_pdf_factura(factura):
    buffer = BytesIO()
    
    # A4 Page size with 2cm left/right margins and 2.5cm top/bottom
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4, 
        rightMargin=2*cm, 
        leftMargin=2*cm, 
        topMargin=2.5*cm, 
        bottomMargin=2.5*cm
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Define Colors
    alired = colors.HexColor("#E62E04")
    aliblack = colors.HexColor("#222222")
    aligrey = colors.HexColor("#666666")
    alibg = colors.HexColor("#F8F8F8")
    aliborder = colors.HexColor("#EBEBEB")
    
    # Custom Paragraph Styles
    base_style = ParagraphStyle(
        'BaseStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=aliblack,
        leading=14
    )
    
    title_right = ParagraphStyle(
        'TitleRight',
        parent=base_style,
        fontName='Helvetica-Bold',
        fontSize=20,
        alignment=2, # Right
        spaceAfter=4
    )
    
    subtitle_right = ParagraphStyle(
        'SubtitleRight',
        parent=base_style,
        textColor=aligrey,
        alignment=2 # Right
    )
    
    logo_style = ParagraphStyle(
        'LogoStyle',
        parent=base_style,
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=alired,
        alignment=1 # Center
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=base_style,
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=8
    )
    
    small_grey = ParagraphStyle(
        'SmallGrey',
        parent=base_style,
        fontSize=8,
        textColor=aligrey,
        leading=10
    )
    
    center_small_grey = ParagraphStyle(
        'CenterSmallGrey',
        parent=small_grey,
        alignment=1
    )

    # --- STORE INFO ---
    tienda_nombre = "TIENDA EN LÍNEA"
    tienda_desc = "Venta de productos en línea"
    store_address = ""
    logo_element = ""
    if connection.schema_name != 'public':
        try:
            tenant = Client.objects.get(schema_name=connection.schema_name)
            tienda_nombre = (tenant.nombre_comercial or tenant.name).upper()
            tienda_desc = "Tienda Oficial"
            logo_path = None
            if tenant.icono and hasattr(tenant.icono, 'path'):
                logo_path = tenant.icono.path
            elif tenant.logo_url:
                logo_path = tenant.logo_url
                
            if logo_path:
                try:
                    logo_element = Image(logo_path, width=4*cm, height=2*cm, kind='proportional')
                except Exception as e:
                    print("Error cargando logo:", e)
        except Client.DoesNotExist:
            pass

    # --- 1. HEADER (Logo & Order Receipt) ---
    logo_table = Table([[logo_element]], colWidths=[4.5*cm], rowHeights=[2.5*cm])
    logo_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    
    fecha_impresion = localtime().strftime("%d %b %Y")
    
    header_data = [
        [
            logo_table,
            [
                Paragraph("<b>Order Receipt</b>", title_right),
                Paragraph(f"Impreso el: {fecha_impresion}", subtitle_right)
            ]
        ]
    ]
    
    header_table = Table(header_data, colWidths=[8.5*cm, 8.5*cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 1*cm))
    
    # --- 2. ORDER DETAILS (Grey Table) ---
    order_date = factura.fecha.strftime("%b %d, %Y")
    # Intentamos obtener el tipo de pago de la factura, o genérico
    payment_method = "Tarjeta / Online"
    if hasattr(factura, 'tipo_pago') and factura.tipo_pago:
        payment_method = factura.tipo_pago.nombre
    elif factura.estado == 'PENDIENTE':
        payment_method = "Pendiente de Pago"

    order_details_data = [
        [
            Paragraph("<b>ORDER ID</b>", small_grey),
            Paragraph("<b>ORDER DATE</b>", small_grey),
            Paragraph("<b>PAYMENT METHOD</b>", small_grey)
        ],
        [
            Paragraph(f"<b># {factura.nro}</b>", base_style),
            Paragraph(f"<b>{order_date}</b>", base_style),
            Paragraph(f"<b>{payment_method}</b>", base_style)
        ]
    ]
    
    order_details_table = Table(order_details_data, colWidths=[5.6*cm, 5.6*cm, 5.8*cm])
    order_details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), alibg),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(order_details_table)
    elements.append(Spacer(1, 1*cm))
    
    # --- 3. ADDRESSES ---
    cliente_nombre = factura.cliente.nombre if factura.cliente else "Consumidor Final"
    cliente_correo = factura.cliente.correo if factura.cliente else ""
    cliente_tel = getattr(factura.cliente, 'telefono', '') if factura.cliente else ""
    
    shipping_text = f"<b>{cliente_nombre}</b><br/>"
    if cliente_correo: shipping_text += f"{cliente_correo}<br/>"
    if cliente_tel: shipping_text += f"Tel: {cliente_tel}"
    
    address_data = [
        [
            Paragraph("<b>Dirección de Facturación</b>", heading_style),
            Paragraph("<b>Información de la Tienda</b>", heading_style)
        ],
        [
            Paragraph(shipping_text, base_style),
            Paragraph(f"<b>{tienda_nombre}</b><br/>{tienda_desc}", base_style)
        ]
    ]
    
    address_table = Table(address_data, colWidths=[8.5*cm, 8.5*cm])
    address_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    
    elements.append(address_table)
    elements.append(Spacer(1, 1.2*cm))
    
    # --- 4. ORDER DETAILS (Products Table) ---
    elements.append(Paragraph("<b>Order Details</b>", heading_style))
    elements.append(Spacer(1, 0.3*cm))
    
    products_data = [
        [
            Paragraph("<b>Item No.</b>", base_style),
            Paragraph("<b>Product Details</b>", base_style),
            Paragraph("<b>Qty</b>", ParagraphStyle('C', parent=base_style, alignment=1)),
            Paragraph("<b>Amount</b>", ParagraphStyle('R', parent=base_style, alignment=2))
        ]
    ]
    
    total = 0
    item_no = 1
    if factura.pedido and factura.pedido.carrito:
        for item in factura.pedido.carrito.items.all():
            p_unit = getattr(item, 'precio_unitario', item.producto.precio)
            subtotal = getattr(item, 'subtotal', p_unit * item.cantidad)
            total += subtotal
            
            prod_desc = f"<b>{item.producto.nombre}</b>"
            # Puedes agregar variaciones si tuvieras aquí
            
            products_data.append([
                Paragraph(str(item_no), base_style),
                Paragraph(prod_desc, base_style),
                Paragraph(str(item.cantidad), ParagraphStyle('C', parent=base_style, alignment=1)),
                Paragraph(f"Bs. {float(subtotal):.2f}", ParagraphStyle('R', parent=base_style, alignment=2))
            ])
            item_no += 1
            
    if total == 0:
        total = factura.monto_total

    products_table = Table(products_data, colWidths=[2*cm, 10*cm, 2*cm, 3*cm])
    
    # Construcción dinámica de estilos de tabla
    pt_styles = [
        ('BACKGROUND', (0,0), (-1,0), alibg),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,0), 1, aliborder),
    ]
    
    # Líneas separadoras entre productos
    for i in range(1, len(products_data)):
        pt_styles.append(('LINEBELOW', (0,i), (-1,i), 1, aliborder))
        
    products_table.setStyle(TableStyle(pt_styles))
    elements.append(products_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # --- 5. PAYMENT SUMMARY ---
    summary_data = [
        [Paragraph("Subtotal:", base_style), Paragraph(f"Bs. {float(total):.2f}", ParagraphStyle('R', parent=base_style, alignment=2))],
        [Paragraph("Shipping Fee:", base_style), Paragraph(f"Bs. 0.00", ParagraphStyle('R', parent=base_style, alignment=2))],
        [Paragraph("Tax:", base_style), Paragraph(f"Bs. 0.00", ParagraphStyle('R', parent=base_style, alignment=2))],
    ]
    
    summary_table1 = Table(summary_data, colWidths=[4*cm, 3.5*cm])
    summary_table1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,-1), (-1,-1), 1, aliborder),
    ]))
    
    total_data = [
        [Paragraph("<b>Order Total:</b>", heading_style), Paragraph(f"<b>Bs. {float(factura.monto_total):.2f}</b>", ParagraphStyle('TR', parent=heading_style, alignment=2, textColor=alired))]
    ]
    summary_table2 = Table(total_data, colWidths=[4*cm, 3.5*cm])
    summary_table2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    
    # Wrap in a mini-table to align right
    layout_table = Table([[ "", [summary_table1, summary_table2] ]], colWidths=[9.5*cm, 7.5*cm])
    layout_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    
    elements.append(layout_table)
    elements.append(Spacer(1, 2*cm))
    
    # --- 6. LOGISTICS INFO ---
    elements.append(Paragraph("<b>Información del Pedido</b>", heading_style))
    elements.append(Spacer(1, 0.2*cm))
    
    tracking_text = (
        "<b>Estado Actual:</b> " + factura.estado + "<br/>"
        "<b>Identificador de Transacción:</b> " + str(factura.nro) + "<br/>"
        "<font color='#666666' size='8'>Puedes consultar los detalles desde tu cuenta.</font>"
    )
    
    tracking_box = Table([[Paragraph(tracking_text, base_style)]], colWidths=[17*cm])
    tracking_box.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, aliblack),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    elements.append(KeepTogether([tracking_box]))
    
    elements.append(Spacer(1, 1*cm))
    
    # --- 7. FOOTER ---
    footer_text = (
        "If you have any questions about this order, please contact the seller.<br/>"
        "Buyer Protection guarantees your purchase. For details, visit our Help Center.<br/>"
        "<b>Thank you for shopping with us!</b>"
    )
    elements.append(Paragraph(footer_text, center_small_grey))
    
    # Build Document
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
