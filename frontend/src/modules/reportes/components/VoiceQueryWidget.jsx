import React, { useState, useRef } from 'react';
import api from 'core/services/api';
import DataTable from 'shared/widgets/DataTable/DataTable';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { FileText, Download, Mic, Square, Loader2 } from 'lucide-react';
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

    const exportToPDF = () => {
        if (!result || !result.results) return;

        const doc = new jsPDF();
        const tableColumn = Object.keys(result.results[0]).map(key => 
            key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
        );
        const tableRows = result.results.map(row => Object.values(row));

        doc.setFontSize(18);
        doc.text("Reporte de Consulta por Voz", 14, 22);
        doc.setFontSize(11);
        doc.setTextColor(100);
        doc.text(`Consulta: ${result.prompt}`, 14, 30);
        doc.text(`Fecha: ${new Date().toLocaleString()}`, 14, 36);

        doc.autoTable({
            startY: 45,
            head: [tableColumn],
            body: tableRows,
            theme: 'grid',
            headStyles: { fillColor: [41, 128, 185], textColor: 255 },
            alternateRowStyles: { fillColor: [245, 245, 245] }
        });

        doc.save(`reporte_${Date.now()}.pdf`);
    };

    const sendAudio = async (blob) => {
        setLoading(true);
        const formData = new FormData();
        formData.append('audio', blob, 'query.webm');

        try {
            // Usamos el endpoint que creamos en el backend
            const response = await api.post('vquery/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setResult(response.data);
            setError(null);
        } catch (err) {
            console.error('Error sending audio:', err);
            const msg = err.response?.data?.error || 'Error al procesar la consulta por voz. Verifica tu conexión y llaves de API.';
            setError(msg);
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <div className={styles.info}>
                    <h3>Asistente de Reportes IA</h3>
                    <p>Haz consultas hablando. Ejemplo: "¿Cuáles son los 5 productos con más stock?"</p>
                </div>
                <div className={styles.controls}>
                    {isRecording ? (
                        <Button 
                            variant="danger" 
                            onClick={stopRecording}
                            leftIcon={<Square size={18} />}
                            className={styles.recordBtn}
                        >
                            Detener y Consultar
                        </Button>
                    ) : (
                        <Button 
                            variant="primary" 
                            onClick={startRecording}
                            disabled={loading}
                            leftIcon={loading ? <Loader2 className="animate-spin" size={18} /> : <Mic size={18} />}
                            className={styles.recordBtn}
                        >
                            {loading ? 'IA Pensando...' : 'Iniciar Consulta por Voz'}
                        </Button>
                    )}
                </div>
            </div>

            {error && <Alert variant="danger" className={styles.alert}>{error}</Alert>}

            {result && (
                <div className={styles.resultContainer}>
                    <div className={styles.resultHeader}>
                        <div className={styles.queryInfo}>
                            <p><strong>Lo que entendí:</strong> "{result.prompt}"</p>
                        </div>
                        {result.results && result.results.length > 0 && (
                            <Button 
                                variant="success" 
                                onClick={exportToPDF}
                                leftIcon={<Download size={18} />}
                            >
                                Descargar PDF
                            </Button>
                        )}
                    </div>

                    {result.results && result.results.length > 0 ? (
                        <div className={styles.tableWrapper}>
                            <DataTable
                                title="Datos Encontrados"
                                data={result.results}
                                columns={Object.keys(result.results[0]).map(key => ({
                                    key,
                                    label: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')
                                }))}
                                compact
                            />
                        </div>
                    ) : (
                        <Alert variant="info">No se encontraron resultados para esta consulta.</Alert>
                    )}
                </div>
            )}
        </div>
    );
};

export default VoiceQueryWidget;
