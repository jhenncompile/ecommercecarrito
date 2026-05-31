import React, { useState } from 'react';
import api from 'core/services/api';
import DataTable from 'shared/widgets/DataTable/DataTable';
import { Button, Alert, Spinner } from 'shared/components';
import { exportToPDF, exportToExcel } from 'utils/exportUtils';
import { Download, Table, Settings2 } from 'lucide-react';
import ReportChart from './ReportChart';
import { formatReportData } from 'utils/formatters';
import styles from './ReportesEstaticos.module.css'; // Reusing static styles

const MODEL_OPTIONS = {
    pedidos: {
        defaultMetrica: 'total',
        defaultAgruparPor: 'mes',
        metricas: [
            { value: 'total', label: 'Suma Total ($)' },
            { value: 'conteo', label: 'Cantidad de Pedidos' }
        ],
        agrupaciones: [
            { value: 'año', label: 'Año' },
            { value: 'mes', label: 'Mes' },
            { value: 'dia', label: 'Día' },
            { value: 'estado', label: 'Estado del Pedido' },
            { value: 'ninguno', label: 'Ninguno' }
        ]
    },
    productos: {
        defaultMetrica: 'stock',
        defaultAgruparPor: 'categoria',
        metricas: [
            { value: 'stock', label: 'Suma de Stock' },
            { value: 'conteo', label: 'Cantidad de Productos' }
        ],
        agrupaciones: [
            { value: 'categoria', label: 'Categoría' },
            { value: 'ninguno', label: 'Ninguno' }
        ]
    }
};

const ReporteDinamicoBuilder = () => {
    const [config, setConfig] = useState({
        modelo: 'pedidos',
        metrica: MODEL_OPTIONS.pedidos.defaultMetrica,
        agrupar_por: MODEL_OPTIONS.pedidos.defaultAgruparPor,
        filtros: {}
    });
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (field, value) => {
        setConfig(prev => ({ ...prev, [field]: value }));
    };

    const handleModeloChange = (modelo) => {
        const options = MODEL_OPTIONS[modelo];
        setConfig({
            modelo,
            metrica: options.defaultMetrica,
            agrupar_por: options.defaultAgruparPor,
            filtros: {}
        });
    };

    const handleAnalizar = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.post('reportes/builder/', config);
            setData(formatReportData(response.data));
        } catch (err) {
            console.error('Error in dynamic report builder:', err);
            setError(err.response?.data?.error || 'Error al construir el reporte dinámico.');
        } finally {
            setLoading(false);
        }
    };

    const handleExportPDF = () => {
        if (!data.length) return;
        try {
            exportToPDF(data, `Reporte Dinámico (${config.modelo})`);
        } catch (err) {
            setError(err.message);
        }
    };

    const handleExportExcel = () => {
        if (!data.length) return;
        try {
            exportToExcel(data, "Dinámico");
        } catch (err) {
            setError(err.message);
        }
    };

    const formatHeader = (key) => key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');

    return (
        <div className={styles.container}>
            <div className={styles.controls} style={{ flexWrap: 'wrap' }}>
                <div className={styles.formGroup}>
                    <label>Origen de Datos:</label>
                    <select 
                        value={config.modelo} 
                        onChange={(e) => handleModeloChange(e.target.value)}
                        className={styles.select}
                    >
                        <option value="pedidos">Pedidos / Ventas</option>
                        <option value="productos">Inventario / Productos</option>
                    </select>
                </div>
                <div className={styles.formGroup}>
                    <label>Métrica a Calcular:</label>
                    <select 
                        value={config.metrica} 
                        onChange={(e) => handleChange('metrica', e.target.value)}
                        className={styles.select}
                    >
                        {MODEL_OPTIONS[config.modelo].metricas.map(option => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                    </select>
                </div>
                <div className={styles.formGroup}>
                    <label>Agrupar por:</label>
                    <select 
                        value={config.agrupar_por} 
                        onChange={(e) => handleChange('agrupar_por', e.target.value)}
                        className={styles.select}
                    >
                        {MODEL_OPTIONS[config.modelo].agrupaciones.map(option => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                    </select>
                </div>
                <Button 
                    variant="primary" 
                    onClick={handleAnalizar}
                    disabled={loading}
                    leftIcon={loading ? <Spinner size="sm" /> : <Settings2 size={18} />}
                >
                    Analizar Datos
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
                    
                    <ReportChart data={data} title="Gráfico del Reporte Dinámico" />
                    
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
                    <p>Configura las variables y haz clic en "Analizar Datos" para visualizar el reporte.</p>
                </div>
            )}
        </div>
    );
};

export default ReporteDinamicoBuilder;
