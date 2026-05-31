import React, { useState, useEffect } from 'react';
import { X, Settings, CheckCircle } from 'lucide-react';
import styles from './WidgetConfigModal.module.css';

export default function WidgetConfigModal({ metadata, block, onClose, onSave }) {
    // block.config may be null if it's new
    const initialConfig = block.config || {
        tipo_reporte: block.type === 'table' ? 'tabla' : 'grafico',
        modelo: metadata?.modelos?.[0]?.id || '',
        metrica: '',
        agrupar_por: '',
        select: [],
        filtros: { logic: 'and', conditions: [] },
        ordenar_por: '-resultado'
    };

    const [config, setConfig] = useState(initialConfig);

    useEffect(() => {
        // If it's a new config (no metrica or agrupar_por set), auto-set them based on model
        if (!config.metrica || !config.agrupar_por) {
            const modelMeta = metadata?.modelos?.find(m => m.id === config.modelo);
            if (modelMeta) {
                setConfig(prev => ({
                    ...prev,
                    metrica: prev.metrica || modelMeta.metricas[0]?.id || '',
                    agrupar_por: prev.agrupar_por || modelMeta.agrupaciones[0]?.id || '',
                    select: prev.select.length ? prev.select : (modelMeta.campos.slice(0, 3).map(c => c.id) || [])
                }));
            }
        }
    }, [config.modelo, metadata]);

    const handleModelChange = (e) => {
        const newModelo = e.target.value;
        const modelMeta = metadata?.modelos?.find(m => m.id === newModelo);
        setConfig({
            ...config,
            modelo: newModelo,
            metrica: modelMeta?.metricas[0]?.id || '',
            agrupar_por: modelMeta?.agrupaciones[0]?.id || '',
            select: modelMeta?.campos.slice(0, 3).map(c => c.id) || [],
            filtros: { logic: 'and', conditions: [] }
        });
    };

    const toggleSelect = (fieldId) => {
        const newSelect = config.select.includes(fieldId)
            ? config.select.filter(id => id !== fieldId)
            : [...config.select, fieldId];
        setConfig({ ...config, select: newSelect });
    };

    const modelMeta = metadata?.modelos?.find(m => m.id === config.modelo);
    if (!modelMeta) return null;

    return (
        <div className={styles.modalOverlay}>
            <div className={styles.modalContent}>
                <div className={styles.modalHeader}>
                    <div className={styles.modalTitle}>
                        <Settings size={20} />
                        <h3>Configurar {block.title}</h3>
                    </div>
                    <button onClick={onClose} className={styles.closeBtn}><X size={20} /></button>
                </div>

                <div className={styles.modalBody}>
                    <div className={styles.formGroup}>
                        <label>Origen de Datos</label>
                        <select value={config.modelo} onChange={handleModelChange} className={styles.input}>
                            {metadata.modelos.map(m => (
                                <option key={m.id} value={m.id}>{m.nombre}</option>
                            ))}
                        </select>
                    </div>

                    {block.type !== 'table' && (
                        <>
                            <div className={styles.formGroup}>
                                <label>Métrica (Valor Y)</label>
                                <select 
                                    value={config.metrica} 
                                    onChange={e => setConfig({...config, metrica: e.target.value})}
                                    className={styles.input}
                                >
                                    {modelMeta.metricas.map(m => (
                                        <option key={m.id} value={m.id}>{m.nombre}</option>
                                    ))}
                                </select>
                            </div>

                            {block.type !== 'kpi' && (
                                <div className={styles.formGroup}>
                                    <label>Agrupación (Eje X)</label>
                                    <select 
                                        value={config.agrupar_por} 
                                        onChange={e => setConfig({...config, agrupar_por: e.target.value})}
                                        className={styles.input}
                                    >
                                        {modelMeta.agrupaciones.map(m => (
                                            <option key={m.id} value={m.id}>{m.nombre}</option>
                                        ))}
                                    </select>
                                </div>
                            )}
                        </>
                    )}

                    {block.type === 'table' && (
                        <div className={styles.formGroup}>
                            <label>Columnas a mostrar</label>
                            <div className={styles.checkboxGrid}>
                                {modelMeta.campos.map(c => (
                                    <label key={c.id} className={styles.checkboxLabel}>
                                        <input 
                                            type="checkbox" 
                                            checked={config.select.includes(c.id)}
                                            onChange={() => toggleSelect(c.id)}
                                        />
                                        {c.nombre}
                                    </label>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div className={styles.modalFooter}>
                    <button onClick={onClose} className={styles.btnOutline}>Cancelar</button>
                    <button onClick={() => onSave(config)} className={styles.btnPrimary}>
                        <CheckCircle size={18} /> Aplicar y Cargar Datos
                    </button>
                </div>
            </div>
        </div>
    );
}
