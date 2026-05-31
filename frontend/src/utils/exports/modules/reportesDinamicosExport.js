import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

const formatHeader = (key) => {
    return key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
};

const reportesDinamicosExport = {
    /**
     * Genera un PDF estructurado a partir de los bloques de un Dashboard
     * No toma capturas de pantalla, renderiza los datos en formato vectorial (texto/tablas)
     */
    generatePDF: (data, metadata = {}) => {
        const blocks = metadata.blocks;
        if (!blocks || blocks.length === 0) {
            throw new Error("No hay bloques en el dashboard para exportar.");
        }

        const title = metadata.title || "Dashboard Dinámico";
        const doc = new jsPDF();
        
        // --- PORTADA O CABECERA GLOBAL ---
        doc.setFontSize(22);
        doc.setTextColor(41, 128, 185);
        doc.text(title, 14, 25);
        
        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Generado el: ${new Date().toLocaleString()}`, 14, 33);
        if (metadata.globalFilters) {
            doc.text(`Filtros globales: ${metadata.globalFilters}`, 14, 39);
        }

        let currentY = 50;

        // --- ITERAR SOBRE CADA BLOQUE DEL DASHBOARD ---
        blocks.forEach((block, index) => {
            const blockData = block.data;
            if (!blockData || blockData.length === 0) return;

            // Si no cabe en la hoja, nueva página
            if (currentY > 250) {
                doc.addPage();
                currentY = 20;
            }

            // Título del bloque (Widget)
            doc.setFontSize(14);
            doc.setTextColor(52, 73, 94);
            doc.text(`${index + 1}. ${block.title} (${block.type.toUpperCase()})`, 14, currentY);
            currentY += 8;

            // Dependiendo del tipo de widget, formateamos los datos
            if (block.type === 'kpi') {
                // Para KPI, sumar o mostrar el valor único
                const total = blockData.reduce((acc, d) => acc + (Number(d.resultado) || 0), 0);
                doc.setFontSize(24);
                doc.setTextColor(39, 174, 96); // Verde esmeralda
                doc.text(total.toLocaleString(), 14, currentY + 10);
                currentY += 25;
            } else {
                // Para barras, pastel, tabla, líneas -> Construir una tabla con los datos crudos
                let tableColumn = [];
                let tableRows = [];

                if (block.type === 'table') {
                    // Usar las columnas seleccionadas en la configuración
                    tableColumn = block.config?.select?.map(formatHeader) || Object.keys(blockData[0]).map(formatHeader);
                    tableRows = blockData.map(row => 
                        tableColumn.map(k => String(row[k.toLowerCase().replace(/ /g, '_')] || '—'))
                    );
                } else {
                    // Para gráficos genéricos del backend (grupo vs resultado)
                    tableColumn = ['Grupo / Eje X', 'Métrica / Eje Y'];
                    tableRows = blockData.map(d => [String(d.grupo || 'General'), String(d.resultado || '0')]);
                }

                autoTable(doc, {
                    startY: currentY,
                    head: [tableColumn],
                    body: tableRows,
                    theme: 'grid',
                    headStyles: { fillColor: [52, 73, 94], textColor: 255, fontSize: 10 },
                    bodyStyles: { fontSize: 9 },
                    alternateRowStyles: { fillColor: [248, 250, 252] },
                    margin: { horizontal: 14 }
                });

                currentY = doc.lastAutoTable.finalY + 20;
            }
        });

        doc.save(`dashboard_${Date.now()}.pdf`);
    },

    generateExcel: (data, metadata = {}) => {
        const blocks = metadata.blocks;
        if (!blocks || blocks.length === 0) return;

        const workbook = XLSX.utils.book_new();

        blocks.forEach((block, index) => {
            if (!block.data || block.data.length === 0) return;
            
            // Sanitizar nombre de la hoja (máximo 31 caracteres y sin caracteres especiales)
            let sheetName = `${index + 1}_${block.title.substring(0, 25)}`.replace(/[\\/?*\[\]]/g, '');

            let worksheet;
            if (block.type === 'table') {
                worksheet = XLSX.utils.json_to_sheet(block.data);
            } else if (block.type === 'kpi') {
                const total = block.data.reduce((acc, d) => acc + (Number(d.resultado) || 0), 0);
                worksheet = XLSX.utils.json_to_sheet([{ Métrica: block.title, Valor_Total: total }]);
            } else {
                // Bar, Pie, Line -> grupo vs resultado
                const formatted = block.data.map(d => ({
                    'Grupo (Eje X)': d.grupo || 'General',
                    'Valor (Eje Y)': Number(d.resultado) || 0
                }));
                worksheet = XLSX.utils.json_to_sheet(formatted);
            }

            // Ajustar anchos
            const wscols = [{ wch: 30 }, { wch: 20 }, { wch: 20 }];
            worksheet['!cols'] = wscols;

            XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
        });

        const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `dashboard_${Date.now()}.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }
};

export default reportesDinamicosExport;
