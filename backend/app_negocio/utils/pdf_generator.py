from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

def generar_pdf_factura(factura):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, f"FACTURA Nro: {factura.nro}")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, f"Fecha: {factura.fecha.strftime('%d/%m/%Y')}")
    p.drawString(100, height - 90, f"Estado: {factura.estado}")
    
    # Cliente
    p.drawString(100, height - 120, "Detalles del Cliente:")
    if factura.pedido and factura.pedido.cliente:
        p.drawString(120, height - 140, f"Nombre: {factura.pedido.cliente.nombre}")
    
    # Línea divisoria
    p.line(100, height - 160, 500, height - 160)
    
    # Items
    p.drawString(100, height - 180, "Descripción")
    p.drawString(400, height - 180, "Total")
    
    y = height - 200
    if factura.pedido:
        for item in factura.pedido.items.all():
            p.drawString(100, y, f"{item.producto.nombre} x {item.cantidad}")
            p.drawString(400, y, f"Bs. {item.subtotal:.2f}")
            y -= 20
            
    # Total
    p.line(100, y - 10, 500, y - 10)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y - 30, f"TOTAL: Bs. {factura.total:.2f}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer
