import api from 'core/services/api';

/**
 * Orquestador principal para la generación de PDFs
 * Ahora se encarga de empaquetar la petición y enviarla al Backend,
 * el cual responde con un archivo binario (Blob).
 * 
 * @param {string} type Tipo de reporte (dinamico, estatico, facturacion, voz)
 * @param {any} data Los datos crudos (puede ser null si ya van en metadata.blocks)
 * @param {object} metadata Metadatos adicionales (titulo, bloques, filtros, etc.)
 */
export const generatePDF = async (type, data, metadata = {}) => {
    try {
        const payload = {
            format: 'pdf',
            type: type,
            metadata: {
                ...metadata,
                data: data // Por si es reporte estático
            }
        };

        const response = await api.post('reportes/export/', payload, {
            responseType: 'blob' // CRÍTICO: Esperamos un archivo, no JSON
        });

        // Crear una URL temporal para descargar el Blob
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const filename = metadata.title ? `${metadata.title}.pdf` : `export_${Date.now()}.pdf`;
        link.setAttribute('download', filename.replace(/ /g, '_'));
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error(`[ExportOrchestrator] Error generating PDF for type ${type}:`, error);
        // Si el backend devuelve un error, intentar leer el blob como texto/json
        if (error.response && error.response.data instanceof Blob) {
            const reader = new FileReader();
            reader.onload = () => {
                try {
                    const errorData = JSON.parse(reader.result);
                    alert(`Error: ${errorData.error || 'Error al generar el documento'}`);
                } catch(e) {
                    alert('Ocurrió un error inesperado al descargar el documento.');
                }
            };
            reader.readAsText(error.response.data);
        } else {
            alert('Error de conexión o fallo al generar el documento.');
        }
    }
};

/**
 * Orquestador principal para la generación de Excel
 * 
 * @param {string} type Tipo de reporte (dinamico, estatico, facturacion, voz)
 * @param {any} data Los datos crudos (puede ser null si ya van en metadata.blocks)
 * @param {object} metadata Metadatos adicionales
 */
export const generateExcel = async (type, data, metadata = {}) => {
    try {
        const payload = {
            format: 'excel',
            type: type,
            metadata: {
                ...metadata,
                data: data
            }
        };

        const response = await api.post('reportes/export/', payload, {
            responseType: 'blob' // CRÍTICO: Esperamos un archivo
        });

        const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const filename = metadata.title ? `${metadata.title}.xlsx` : `export_${Date.now()}.xlsx`;
        link.setAttribute('download', filename.replace(/ /g, '_'));
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error(`[ExportOrchestrator] Error generating Excel for type ${type}:`, error);
        if (error.response && error.response.data instanceof Blob) {
            const reader = new FileReader();
            reader.onload = () => {
                try {
                    const errorData = JSON.parse(reader.result);
                    alert(`Error: ${errorData.error || 'Error al generar el Excel'}`);
                } catch(e) {
                    alert('Ocurrió un error inesperado al descargar el Excel.');
                }
            };
            reader.readAsText(error.response.data);
        } else {
            alert('Error de conexión o fallo al generar el Excel.');
        }
    }
};
