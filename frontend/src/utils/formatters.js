export const formatReportData = (data) => {
    if (!data || !data.length) return data;
    
    return data.map(row => {
        const newRow = { ...row };
        Object.keys(newRow).forEach(key => {
            const val = newRow[key];
            if (!val) return;
            const valStr = String(val);
            // Si parece una fecha ISO o YYYY-MM-DD
            if (/^\d{4}-\d{2}-\d{2}(T|$)/.test(valStr)) {
                const date = new Date(valStr);
                if (!isNaN(date.getTime())) {
                    if (key === 'mes' || key === 'month') {
                        newRow[key] = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
                    } else if (key === 'año' || key === 'year') {
                        newRow[key] = `${date.getFullYear()}`;
                    } else if (key === 'dia' || key === 'date') {
                        newRow[key] = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                    } else {
                        // Por defecto si es otra clave
                        newRow[key] = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                    }
                }
            }
        });
        return newRow;
    });
};
