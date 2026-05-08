import React, { useState, useRef } from 'react';
import api from 'core/services/api';
import DataTable from 'shared/widgets/DataTable/DataTable';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import * as XLSX from 'xlsx';
import { Download, Mic, Square, Loader2, Table } from 'lucide-react';
import { Button, Alert } from 'shared/components';
import styles from './VoiceQueryWidget.module.css';

const VoiceQueryWidget = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const mediaRecorder = useRef(null);
    const audioChunks = useRef([]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder.current = new MediaRecorder(stream);
            audioChunks.current = [];

            mediaRecorder.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.current.push(event.data);
                }
            };

            mediaRecorder.current.onstop = async () => {
                const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
                sendAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.current.start();
            setIsRecording(true);
            setError(null);
        } catch (err) {
            console.error('Error recording:', err);
            setError('No se pudo acceder al micrófono. Por favor, concede los permisos en el navegador.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorder.current && isRecording) {
            mediaRecorder.current.stop();
            setIsRecording(false);
        }
    };

    const formatHeader = (key) => {
        return key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
    };

    const exportToPDF = () => {
        if (!result || !result.results || result.results.length === 0) return;

        try {
            const doc = new jsPDF();
            const tableColumn = Object.keys(result.results[0]).map(formatHeader);
            const tableRows = result.results.map(row => Object.values(row));

            doc.setFontSize(20);
            doc.setTextColor(41, 128, 185);
            doc.text("Reporte de Consulta Inteligente", 14, 22);
            
            doc.setFontSize(10);
            doc.setTextColor(100);
            doc.text(`Consulta: ${result.prompt}`, 14, 32);
            doc.text(`Generado el: ${new Date().toLocaleString()}`, 14, 38);
            doc.text(`Total registros: ${result.results.length}`, 14, 44);

            doc.autoTable({
                startY: 50,
                head: [tableColumn],
                body: tableRows,
                theme: 'striped',
                headStyles: { fillColor: [44, 62, 80], textColor: 255, fontSize: 10, halign: 'center' },
                bodyStyles: { fontSize: 9 },
                alternateRowStyles: { fillColor: [245, 247, 250] },
                margin: { top: 50 }
            });

            doc.save(`reporte_ia_${Date.now()}.pdf`);
        } catch (err) {
            console.error('Error generating PDF:', err);
            setError('Error al generar el PDF. Inténtalo de nuevo.');
        }
    };

    const exportToExcel = () => {
        if (!result || !result.results || result.results.length === 0) return;

        try {
            const worksheet = XLSX.utils.json_to_sheet(result.results);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, "Reporte IA");
            
            // Ajustar anchos de columna básicos
            const wscols = Object.keys(result.results[0]).map(k => ({ wch: Math.max(k.length, 15) }));
            worksheet['!cols'] = wscols;

            XLSX.writeFile(workbook, `reporte_ia_${Date.now()}.xlsx`);
        } catch (err) {
            console.error('Error generating Excel:', err);
            setError('Error al generar el archivo Excel.');
        }
    };

    const sendAudio = async (blob) => {
        setLoading(true);
        setResult(null);
        const formData = new FormData();
        formData.append('audio', blob, 'query.webm');

        try {
            const response = await api.post('vquery/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
            setError(null);
        } catch (err) {
            console.error('Error sending audio:', err);
            const msg = err.response?.data?.error || 'Error al procesar la consulta. Intenta ser más claro o verifica tu conexión.';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.glassHeader}>
                <div className={styles.titleArea}>
                    <div className={styles.iconCircle}>
                        <Mic size={24} className={isRecording ? styles.pulse : ''} />
                    </div>
                    <div>
                        <h3 className={styles.title}>Asistente de Voz IA</h3>
                        <p className={styles.subtitle}>Genera reportos complejos usando lenguaje natural</p>
                    </div>
                </div>
                
                <div className={styles.actionArea}>
                    {isRecording ? (
                        <Button 
                            variant="danger" 
                            onClick={stopRecording}
                            leftIcon={<Square size={18} />}
                            className={`${styles.mainBtn} ${styles.btnDanger}`}
                        >
                            Detener Grabación
                        </Button>
                    ) : (
                        <Button 
                            variant="primary" 
                            onClick={startRecording}
                            disabled={loading}
                            leftIcon={loading ? <Loader2 className="animate-spin" size={20} /> : <Mic size={20} />}
                            className={styles.mainBtn}
                        >
                            {loading ? 'Analizando...' : 'Hablar ahora'}
                        </Button>
                    )}
                </div>
            </div>

            {error && (
                <div className={styles.errorAlert}>
                    <Alert variant="danger">{error}</Alert>
                </div>
            )}

            {loading && (
                <div className={styles.loadingState}>
                    <div className={styles.spinnerWrapper}>
                        <Loader2 className={styles.spinner} size={40} />
                    </div>
                    <p>Procesando tu voz y consultando la base de datos...</p>
                </div>
            )}

            {result && (
                <div className={styles.resultSection}>
                    <div className={styles.resultMeta}>
                        <div className={styles.promptCard}>
                            <span className={styles.label}>Lo que entendí:</span>
                            <p className={styles.promptText}>"{result.prompt}"</p>
                        </div>
                        
                        <div className={styles.actionButtons}>
                            {result.results && result.results.length > 0 && (
                                <div className={styles.exportButtons}>
                                    <Button 
                                        variant="success" 
                                        size="md"
                                        onClick={exportToExcel}
                                        leftIcon={<Table size={20} />}
                                        className={styles.excelBtn}
                                    >
                                        Descargar Excel
                                    </Button>
                                    <Button 
                                        variant="primary" 
                                        size="md"
                                        onClick={exportToPDF}
                                        leftIcon={<Download size={20} />}
                                    >
                                        Descargar PDF
                                    </Button>
                                </div>
                            )}
                        </div>
                    </div>

                    {result.results && result.results.length > 0 ? (
                        <div className={styles.tableContainer}>
                            <div className={styles.tableHeader}>
                                <span>Resultados encontrados: <strong>{result.results.length}</strong></span>
                            </div>
                            <div className={styles.tableScroll}>
                                <DataTable
                                    data={result.results}
                                    columns={Object.keys(result.results[0]).map(key => ({
                                        key,
                                        label: formatHeader(key)
                                    }))}
                                    compact
                                />
                            </div>
                        </div>
                    ) : (
                        !loading && <div className={styles.emptyState}>No se encontraron datos para esta consulta.</div>
                    )}
                </div>
            )}
            
            {!result && !loading && !error && (
                <div className={styles.helperText}>
                    <span>Sugerencias:</span>
                    <ul>
                        <li>"Muéstrame las ventas de este mes"</li>
                        <li>"¿Cuáles son los productos con menos de 10 unidades en stock?"</li>
                        <li>"Lista los 5 clientes que más han comprado"</li>
                    </ul>
                </div>
            )}
        </div>
    );
};

export default VoiceQueryWidget;
