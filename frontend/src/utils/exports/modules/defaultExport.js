import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

const formatHeader = (key) => {
    return key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
};

const defaultExport = {
    generatePDF: (data, metadata = {}) => {
        if (!data || data.length === 0) return;
        const title = metadata.title || "Reporte de Datos";
        const prompt = metadata.prompt || "";

        try {
            const doc = new jsPDF();
            const tableColumn = Object.keys(data[0]).map(formatHeader);
            
            // Sanitizar datos: convertir objetos a string y manejar nulls
            const tableRows = data.map(row => 
                Object.values(row).map(val => {
                    if (val === null || val === undefined) return '—';
                    if (typeof val === 'object') return JSON.stringify(val);
                    return String(val);
                })
            );

            doc.setFontSize(18);
            doc.setTextColor(41, 128, 185);
            doc.text(title, 14, 22);
            
            doc.setFontSize(10);
            doc.setTextColor(100);
            if (prompt) {
                doc.text(`Consulta: ${prompt}`, 14, 32);
                doc.text(`Generado el: ${new Date().toLocaleString()}`, 14, 38);
                doc.text(`Total registros: ${data.length}`, 14, 44);
            } else {
                doc.text(`Generado el: ${new Date().toLocaleString()}`, 14, 32);
                doc.text(`Total registros: ${data.length}`, 14, 38);
            }

            autoTable(doc, {
                startY: prompt ? 50 : 44,
                head: [tableColumn],
                body: tableRows,
                theme: 'striped',
                headStyles: { fillColor: [44, 62, 80], textColor: 255, fontSize: 9, halign: 'center' },
                bodyStyles: { fontSize: 8 },
                alternateRowStyles: { fillColor: [245, 247, 250] },
                margin: { top: 50, horizontal: 10 },
                styles: { overflow: 'linebreak' }
            });

            doc.save(`reporte_${Date.now()}.pdf`);
        } catch (err) {
            console.error('Error generating PDF:', err);
            throw new Error('Error al generar el PDF. Verifica que los datos no sean demasiado grandes.');
        }
    },

    generateExcel: (data, metadata = {}) => {
        if (!data || data.length === 0) return;
        const sheetName = metadata.title || "Reporte";

        try {
            const worksheet = XLSX.utils.json_to_sheet(data);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
            
            // Ajustar anchos de columna
            const wscols = Object.keys(data[0]).map(k => ({ wch: Math.max(k.length, 15) }));
            worksheet['!cols'] = wscols;

            // Generar buffer
            const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
            const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            
            // Descarga robusta
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `reporte_${Date.now()}.xlsx`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Error generating Excel:', err);
            throw new Error('Error al generar el archivo Excel.');
        }
    }
};

export default defaultExport;
