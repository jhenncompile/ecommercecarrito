import React, { useState } from 'react';
import api from 'core/services/api';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Alert, Spinner } from 'shared/components';
import { generatePDF, generateExcel } from 'utils/exports/exportOrchestrator';
import { Download, Table, BarChart } from 'lucide-react';
import ReportChart from './ReportChart';
import { formatReportData } from 'utils/formatters';
import styles from './ReportesEstaticos.module.css';

const ReportesEstaticos = () => {
    const [tipo, setTipo] = useState('ventas_mensuales');
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleGenerar = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.get(`reportes/estatico/${tipo}/`);
            setData(formatReportData(response.data));
        } catch (err) {
            console.error('Error fetching static report:', err);
            setError(err.response?.data?.error || 'Error al obtener el reporte.');
        } finally {
            setLoading(false);
        }
    };

    const handleExportPDF = () => {
        if (!data.length) return;
        try {
            generatePDF('estatico', data, { title: `Reporte Estático: ${tipo}` });
        } catch (err) {
            setError(err.message);
        }
    };

    const handleExportExcel = () => {
        if (!data.length) return;
        try {
            generateExcel('estatico', data, { title: tipo });
        } catch (err) {
            setError(err.message);
        }
    };

    const formatHeader = (key) => key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');

    return (
        <div className={styles.container}>
            <div className={styles.controls}>
                <div className={styles.formGroup}>
                    <label>Tipo de Reporte:</label>
                    <select 
                        value={tipo} 
                        onChange={(e) => setTipo(e.target.value)}
                        className={styles.select}
                    >
                        <option value="ventas_mensuales">Ventas Mensuales</option>
                        <option value="ventas_anuales">Ventas Anuales</option>
                        <option value="top_productos">Top Productos</option>
                        <option value="top_categorias">Top Categorías</option>
                        <option value="nuevos_clientes">Nuevos Clientes (Mensual)</option>
                        <option value="nuevos_clientes_anual">Nuevos Clientes (Anual)</option>
                    </select>
                </div>
                <Button 
                    variant="primary" 
                    onClick={handleGenerar}
                    disabled={loading}
                    leftIcon={loading ? <Spinner size="sm" /> : <BarChart size={18} />}
                >
                    Generar Reporte
                </Button>
            </div>

            {error && <Alert variant="danger" className={styles.alert}>{error}</Alert>}

            {data.length > 0 && (
                <div className={styles.resultSection}>
                    <div className={styles.actions}>
                        <Button 
                            variant="success" 
                            onClick={handleExportExcel}
                            leftIcon={<Table size={18} />}
                        >
                            Excel
                        </Button>
                        <Button 
                            variant="primary" 
                            onClick={handleExportPDF}
                            leftIcon={<Download size={18} />}
                        >
                            PDF
                        </Button>
                    </div>
                    
                    <ReportChart data={data} title="Gráfico del Reporte Estático" />
                    
                    <div className={styles.tableWrapper}>
                        <DataTable
                            data={data}
                            columns={Object.keys(data[0]).map(key => ({
                                key,
                                label: formatHeader(key)
                            }))}
                            compact
                        />
                    </div>
                </div>
            )}
            {!loading && data.length === 0 && !error && (
                <div className={styles.emptyState}>
                    <p>Selecciona un reporte y haz clic en "Generar Reporte" para ver los datos.</p>
                </div>
            )}
        </div>
    );
};

export default ReportesEstaticos;
