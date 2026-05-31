import jsPDF from 'jspdf';

const reportesVozExport = {
    /**
     * Módulo especializado para exportar reportes generados a partir de comandos de voz.
     * Generalmente estos son reportes ejecutivos o resúmenes en texto natural (párrafos).
     */
    generatePDF: (data, metadata = {}) => {
        // ESQUELETO PREPARADO PARA FUTURA IMPLEMENTACIÓN
        console.log("Iniciando motor de exportación de REPORTES POR VOZ...");
        const doc = new jsPDF();
        
        const transcripcion = metadata.transcripcion || "Resumen ejecutivo generado por asistente de voz.";
        
        doc.setFontSize(22);
        doc.setTextColor(44, 62, 80);
        doc.text("Resumen Ejecutivo (Asistente de Voz)", 14, 25);
        
        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Generado el: ${new Date().toLocaleString()}`, 14, 33);
        
        // Bloque de texto largo (Wrap)
        doc.setFontSize(12);
        doc.setTextColor(50, 50, 50);
        
        const splitTitle = doc.splitTextToSize(transcripcion, 180);
        doc.text(splitTitle, 14, 50);

        // Si data incluye cuadros estadísticos extraídos por la IA, se podrían añadir tablas aquí abajo.

        doc.save(`reporte_voz_${Date.now()}.pdf`);
    },

    generateExcel: (data, metadata = {}) => {
        // No tiene mucho sentido exportar un resumen ejecutivo en texto a excel, 
        // pero se deja la firma implementada por cumplimiento de interfaz.
        console.warn("Exportación Excel de reportes por voz no implementada.");
    }
};

export default reportesVozExport;
