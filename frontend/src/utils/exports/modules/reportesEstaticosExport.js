import defaultExport from './defaultExport';

const reportesEstaticosExport = {
    generatePDF: (data, metadata = {}) => {
        // En el futuro, aquí se puede agregar una portada específica para reportes estáticos,
        // tablas de contenido, o un diseño tabular mucho más avanzado.
        // Por ahora, reutilizamos la lógica probada de tablas estáticas.
        return defaultExport.generatePDF(data, {
            ...metadata,
            title: metadata.title || "Reporte Estático"
        });
    },

    generateExcel: (data, metadata = {}) => {
        return defaultExport.generateExcel(data, {
            ...metadata,
            title: metadata.title || "Reporte_Estatico"
        });
    }
};

export default reportesEstaticosExport;
