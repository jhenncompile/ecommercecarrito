import React, { useState } from 'react';
import { Calendar, ChevronDown, Check } from 'lucide-react';
import styles from './DateFilter.module.css';

const DateFilter = ({ onFilterChange }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedRange, setSelectedRange] = useState('all');
    
    // Si es "custom", mostramos los inputs
    const [customStart, setCustomStart] = useState('');
    const [customEnd, setCustomEnd] = useState('');

    const ranges = [
        { id: 'all', label: 'Todo el tiempo' },
        { id: 'today', label: 'Hoy' },
        { id: 'week', label: 'Últimos 7 días' },
        { id: 'month', label: 'Este mes' },
        { id: 'year', label: 'Este año' },
        { id: 'custom', label: 'Rango Exacto...' },
    ];

    const applyFilter = (rangeId, start = '', end = '') => {
        setSelectedRange(rangeId);
        
        const now = new Date();
        let computedStart = null;
        let computedEnd = null;

        if (rangeId === 'today') {
            computedStart = now.toISOString().split('T')[0];
            computedEnd = computedStart;
        } else if (rangeId === 'week') {
            const lastWeek = new Date(now);
            lastWeek.setDate(now.getDate() - 7);
            computedStart = lastWeek.toISOString().split('T')[0];
            computedEnd = now.toISOString().split('T')[0];
        } else if (rangeId === 'month') {
            computedStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
            computedEnd = now.toISOString().split('T')[0];
        } else if (rangeId === 'year') {
            computedStart = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
            computedEnd = now.toISOString().split('T')[0];
        } else if (rangeId === 'custom') {
            computedStart = start;
            computedEnd = end;
        }

        const newConditions = [];
        if (computedStart) {
            newConditions.push({ field: 'fecha_creacion', operator: 'gte', value: computedStart });
        }
        if (computedEnd) {
            newConditions.push({ field: 'fecha_creacion', operator: 'lte', value: computedEnd });
        }
        
        onFilterChange(newConditions);
        if (rangeId !== 'custom') setIsOpen(false);
    };

    return (
        <div className={styles.dateFilterContainer}>
            <button 
                className={styles.triggerButton} 
                onClick={() => setIsOpen(!isOpen)}
                type="button"
            >
                <Calendar size={16} />
                <span>{ranges.find(r => r.id === selectedRange)?.label}</span>
                <ChevronDown size={16} />
            </button>

            {isOpen && (
                <div className={styles.dropdownPanel}>
                    <div className={styles.rangeList}>
                        {ranges.map(range => (
                            <button
                                key={range.id}
                                className={`${styles.rangeOption} ${selectedRange === range.id ? styles.active : ''}`}
                                onClick={() => applyFilter(range.id, customStart, customEnd)}
                            >
                                {range.label}
                                {selectedRange === range.id && <Check size={14} className={styles.checkIcon} />}
                            </button>
                        ))}
                    </div>
                    
                    {selectedRange === 'custom' && (
                        <div className={styles.customPanel}>
                            <label>
                                Desde:
                                <input 
                                    type="date" 
                                    value={customStart}
                                    onChange={(e) => {
                                        setCustomStart(e.target.value);
                                        applyFilter('custom', e.target.value, customEnd);
                                    }} 
                                />
                            </label>
                            <label>
                                Hasta:
                                <input 
                                    type="date" 
                                    value={customEnd}
                                    onChange={(e) => {
                                        setCustomEnd(e.target.value);
                                        applyFilter('custom', customStart, e.target.value);
                                    }} 
                                />
                            </label>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default DateFilter;
