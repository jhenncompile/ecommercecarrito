import React, { useState } from 'react';
import { 
    DndContext, 
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragOverlay,
    useDraggable,
    useDroppable
} from '@dnd-kit/core';
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    verticalListSortingStrategy,
} from '@dnd-kit/sortable';

import { Trash2, GripVertical, Database, Filter, Layers, BarChart2, ArrowDownUp, X, Table, PieChart } from 'lucide-react';
import styles from './QueryBuilder.module.css';
import SortableColumn from './SortableColumn';
import DateFilter from './DateFilter';

// --- SUBCOMPONENTES DND-KIT ---

const DraggablePill = ({ id, payload, className, children }) => {
    const {attributes, listeners, setNodeRef, transform, isDragging} = useDraggable({
        id: id,
        data: payload
    });
    
    // We don't apply transform here so it stays in place in the sidebar, 
    // but we use DragOverlay to show what's being dragged.
    const style = {
        opacity: isDragging ? 0.4 : 1,
        cursor: 'grab'
    };

    return (
        <div ref={setNodeRef} style={style} {...listeners} {...attributes} className={className}>
            {children}
        </div>
    );
};

const DroppableZone = ({ id, className, activeClassName, children }) => {
    const {isOver, setNodeRef} = useDroppable({ id });
    return (
        <div ref={setNodeRef} className={`${className} ${isOver ? activeClassName : ''}`}>
            {children}
        </div>
    );
};


// --- MAIN COMPONENT ---

const QueryBuilder = ({ metadata, config, onChange }) => {
    const [activeId, setActiveId] = useState(null);
    const [activePayload, setActivePayload] = useState(null);

    const sensors = useSensors(
        useSensor(PointerSensor, {
            activationConstraint: { distance: 5 }, // 5px tolerance before dragging starts
        }),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    const currentConfig = {
        tipo_reporte: config.tipo_reporte || 'tabla',
        modelo: config.modelo || (metadata?.modelos?.[0]?.id || ''),
        filtros: config.filtros?.logic ? config.filtros : { logic: 'and', conditions: [] },
        agrupar_por: config.agrupar_por || '',
        metrica: config.metrica || '',
        ordenar_por: config.ordenar_por || '-resultado',
        select: config.select || [],
        ...config
    };

    const currentModelMeta = metadata?.modelos?.find(m => m.id === currentConfig.modelo);

    const handleModelChange = (e) => {
        const newModelo = e.target.value;
        const newModelMeta = metadata.modelos.find(m => m.id === newModelo);
        onChange({
            ...currentConfig,
            modelo: newModelo,
            agrupar_por: newModelMeta?.agrupaciones[0]?.id || '',
            metrica: newModelMeta?.metricas[0]?.id || '',
            select: newModelMeta?.campos.slice(0, 3).map(c => c.id) || [], // select first 3 by default
            ordenar_por: '-resultado',
            filtros: { logic: 'and', conditions: [] }
        });
    };

    const handleTabChange = (tipo) => {
        onChange({ ...currentConfig, tipo_reporte: tipo });
    };

    const handleDragStart = (event) => {
        const { active } = event;
        setActiveId(active.id);
        setActivePayload(active.data.current);
    };

    const handleDragEnd = (event) => {
        const { active, over } = event;
        setActiveId(null);
        setActivePayload(null);

        if (!over) return;

        // 1. REORDER COLUMNS (SortableContext)
        if (active.data.current?.sortable && over.data.current?.sortable) {
            if (active.id !== over.id) {
                const oldIndex = currentConfig.select.indexOf(active.id);
                const newIndex = currentConfig.select.indexOf(over.id);
                const newSelect = arrayMove(currentConfig.select, oldIndex, newIndex);
                onChange({ ...currentConfig, select: newSelect });
            }
            return;
        }

        // 2. DROP PILL INTO ZONES
        const draggedType = active.data.current?.type;
        const draggedItem = active.data.current?.item;
        
        if (!draggedItem) return;

        const zoneId = over.id;

        if (zoneId === 'zone_agrupar' && draggedType === 'agrupacion') {
            onChange({ ...currentConfig, agrupar_por: draggedItem.id });
        } 
        else if (zoneId === 'zone_metrica' && draggedType === 'metrica') {
            onChange({ ...currentConfig, metrica: draggedItem.id });
        } 
        else if (zoneId === 'zone_filtros' && draggedType === 'campo') {
            const newCondition = { field: draggedItem.id, operator: 'exact', value: '' };
            onChange({
                ...currentConfig,
                filtros: {
                    ...currentConfig.filtros,
                    conditions: [...currentConfig.filtros.conditions, newCondition]
                }
            });
        }
        else if (zoneId === 'zone_columnas' && draggedType === 'campo') {
            if (!currentConfig.select.includes(draggedItem.id)) {
                onChange({ ...currentConfig, select: [...currentConfig.select, draggedItem.id] });
            }
        }
    };

    // Filter Logic
    const updateCondition = (index, key, value) => {
        const newConditions = [...currentConfig.filtros.conditions];
        newConditions[index] = { ...newConditions[index], [key]: value };
        if (key === 'field') {
            newConditions[index].operator = 'exact';
            newConditions[index].value = '';
        }
        onChange({ ...currentConfig, filtros: { ...currentConfig.filtros, conditions: newConditions } });
    };

    const removeCondition = (index) => {
        const newConditions = currentConfig.filtros.conditions.filter((_, i) => i !== index);
        onChange({ ...currentConfig, filtros: { ...currentConfig.filtros, conditions: newConditions } });
    };

    const handleDateFilterChange = (newConditions) => {
        // Remove existing date filters
        const filteredConditions = currentConfig.filtros.conditions.filter(c => c.field !== 'fecha_creacion');
        // Add new ones
        onChange({
            ...currentConfig,
            filtros: {
                ...currentConfig.filtros,
                conditions: [...filteredConditions, ...newConditions]
            }
        });
    };

    const removeColumn = (colId) => {
        onChange({ ...currentConfig, select: currentConfig.select.filter(id => id !== colId) });
    };

    if (!metadata || !currentModelMeta) return <div className={styles.loading}>Preparando entorno...</div>;

    const activeAgrupacion = currentModelMeta.agrupaciones.find(a => a.id === currentConfig.agrupar_por)?.nombre || 'Ninguno';
    const activeMetrica = currentModelMeta.metricas.find(m => m.id === currentConfig.metrica)?.nombre || 'No seleccionado';

    return (
        <DndContext sensors={sensors} collisionDetection={closestCenter} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            
            <div className={styles.tabsContainer}>
                <button 
                    className={`${styles.tabBtn} ${currentConfig.tipo_reporte === 'tabla' ? styles.activeTab : ''}`}
                    onClick={() => handleTabChange('tabla')}
                >
                    <Table size={18} /> Tabla de Datos
                </button>
                <button 
                    className={`${styles.tabBtn} ${currentConfig.tipo_reporte === 'grafico' ? styles.activeTab : ''}`}
                    onClick={() => handleTabChange('grafico')}
                >
                    <PieChart size={18} /> Reporte Gráfico
                </button>
            </div>

            <div className={styles.dndLayout}>
                
                {/* PANEL IZQUIERDO: BIBLIOTECA */}
                <div className={styles.sidebar}>
                    <div className={styles.sidebarSection}>
                        <div className={styles.sidebarHeader}>
                            <Database size={18} /> Origen de Datos
                        </div>
                        <select value={currentConfig.modelo} onChange={handleModelChange} className={styles.sourceSelect}>
                            {metadata.modelos.map(m => (
                                <option key={m.id} value={m.id}>{m.nombre}</option>
                            ))}
                        </select>
                    </div>

                    <div className={styles.pillsContainer}>
                        {currentConfig.tipo_reporte === 'grafico' && (
                            <>
                                <h4 className={styles.pillsTitle}>Métricas</h4>
                                <div className={styles.pillsGrid}>
                                    {currentModelMeta.metricas.map(m => (
                                        <DraggablePill key={`m_${m.id}`} id={`m_${m.id}`} payload={{ type: 'metrica', item: m }} className={`${styles.dragPill} ${styles.pillMetrica}`}>
                                            <GripVertical size={14} className={styles.gripIcon}/> {m.nombre}
                                        </DraggablePill>
                                    ))}
                                </div>

                                <h4 className={styles.pillsTitle}>Agrupaciones</h4>
                                <div className={styles.pillsGrid}>
                                    {currentModelMeta.agrupaciones.map(a => (
                                        <DraggablePill key={`a_${a.id}`} id={`a_${a.id}`} payload={{ type: 'agrupacion', item: a }} className={`${styles.dragPill} ${styles.pillAgrupacion}`}>
                                            <GripVertical size={14} className={styles.gripIcon}/> {a.nombre}
                                        </DraggablePill>
                                    ))}
                                </div>
                            </>
                        )}

                        <h4 className={styles.pillsTitle}>Campos (Filtros {currentConfig.tipo_reporte === 'tabla' && '& Columnas'})</h4>
                        <div className={styles.pillsGrid}>
                            {currentModelMeta.campos.map(c => (
                                <DraggablePill key={`c_${c.id}`} id={`c_${c.id}`} payload={{ type: 'campo', item: c }} className={`${styles.dragPill} ${styles.pillCampo}`}>
                                    <GripVertical size={14} className={styles.gripIcon}/> {c.nombre}
                                </DraggablePill>
                            ))}
                        </div>
                    </div>
                </div>

                {/* LIENZO PRINCIPAL */}
                <div className={styles.canvas}>
                    
                    <div className={styles.canvasToolbar}>
                        <DateFilter onFilterChange={handleDateFilterChange} />
                    </div>

                    {currentConfig.tipo_reporte === 'grafico' ? (
                        <div className={styles.canvasGridTop}>
                            <DroppableZone id="zone_metrica" className={styles.dropZone} activeClassName={styles.dropZoneActive}>
                                <div className={styles.zoneHeader}><BarChart2 size={18} /> Métrica (Eje Y)</div>
                                <div className={styles.zoneContent}>
                                    <div className={`${styles.activePill} ${styles.activeMetrica}`}>{activeMetrica}</div>
                                </div>
                            </DroppableZone>

                            <DroppableZone id="zone_agrupar" className={styles.dropZone} activeClassName={styles.dropZoneActive}>
                                <div className={styles.zoneHeader}><Layers size={18} /> Agrupación (Eje X)</div>
                                <div className={styles.zoneContent}>
                                    <div className={`${styles.activePill} ${styles.activeAgrupacion}`}>{activeAgrupacion}</div>
                                </div>
                            </DroppableZone>
                        </div>
                    ) : (
                        <DroppableZone id="zone_columnas" className={styles.dropZone} activeClassName={styles.dropZoneActive}>
                            <div className={styles.zoneHeader}><Table size={18} /> Columnas Activas (Arrastra para reordenar o añadir)</div>
                            
                            <div className={styles.sortableListContainer}>
                                <SortableContext items={currentConfig.select} strategy={verticalListSortingStrategy}>
                                    {currentConfig.select.map(colId => {
                                        const fieldInfo = currentModelMeta.campos.find(c => c.id === colId);
                                        return (
                                            <SortableColumn 
                                                key={colId} 
                                                id={colId} 
                                                label={fieldInfo?.nombre || colId} 
                                                onRemove={removeColumn} 
                                            />
                                        );
                                    })}
                                </SortableContext>
                                {currentConfig.select.length === 0 && (
                                    <p className={styles.emptyZoneText}>Arrastra campos naranjas aquí para agregarlos a la tabla.</p>
                                )}
                            </div>
                        </DroppableZone>
                    )}

                    {/* ZONA DE FILTROS */}
                    <DroppableZone id="zone_filtros" className={`${styles.dropZone} ${styles.filtersDropZone}`} activeClassName={styles.dropZoneActive}>
                        <div className={styles.zoneHeader}><Filter size={18} /> Filtros por Condición (Arrastra campos aquí)</div>
                        
                        {currentConfig.filtros.conditions.length === 0 ? (
                            <div className={styles.emptyZoneText}>Arrastra campos naranjas aquí para crear reglas específicas.</div>
                        ) : (
                            <div className={styles.filtersList}>
                                {currentConfig.filtros.conditions.length > 1 && (
                                    <div className={styles.logicToggle}>
                                        Operador Lógico: 
                                        <select 
                                            value={currentConfig.filtros.logic} 
                                            onChange={(e) => onChange({ ...currentConfig, filtros: { ...currentConfig.filtros, logic: e.target.value } })} 
                                            className={styles.orderSelect}
                                            style={{marginLeft: '0.5rem'}}
                                        >
                                            <option value="and">Debe cumplir TODAS las reglas (Y)</option>
                                            <option value="or">Debe cumplir ALGUNA regla (O)</option>
                                        </select>
                                    </div>
                                )}

                                {currentConfig.filtros.conditions.map((cond, index) => {
                                    const selectedField = currentModelMeta.campos.find(c => c.id === cond.field);
                                    const fieldType = selectedField?.tipo || 'string';
                                    const availableOperators = metadata.operadores[fieldType] || [];

                                    return (
                                        <div key={index} className={styles.filterCard}>
                                            <div className={styles.filterFieldBadge}>{selectedField?.nombre || cond.field}</div>
                                            <select value={cond.operator} onChange={(e) => updateCondition(index, 'operator', e.target.value)} className={styles.filterSelect}>
                                                {availableOperators.map(op => <option key={op.id} value={op.id}>{op.nombre}</option>)}
                                            </select>
                                            {selectedField?.opciones ? (
                                                <select value={cond.value} onChange={(e) => updateCondition(index, 'value', e.target.value)} className={styles.filterInput}>
                                                    <option value="">Seleccione...</option>
                                                    {selectedField.opciones.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                                                </select>
                                            ) : fieldType === 'date' ? (
                                                <input type="date" value={cond.value} onChange={(e) => updateCondition(index, 'value', e.target.value)} className={styles.filterInput} />
                                            ) : fieldType === 'number' ? (
                                                <input type="number" value={cond.value} onChange={(e) => updateCondition(index, 'value', e.target.value)} className={styles.filterInput} />
                                            ) : (
                                                <input type="text" value={cond.value} onChange={(e) => updateCondition(index, 'value', e.target.value)} className={styles.filterInput} />
                                            )}
                                            <button className={styles.filterRemoveBtn} onClick={() => removeCondition(index)}><X size={18} /></button>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </DroppableZone>
                </div>
            </div>

            <DragOverlay>
                {activeId ? (
                    <div className={`${styles.dragPill} ${activePayload?.type === 'metrica' ? styles.pillMetrica : activePayload?.type === 'agrupacion' ? styles.pillAgrupacion : styles.pillCampo} ${styles.draggingPill}`}>
                        <GripVertical size={14} /> {activePayload?.item?.nombre}
                    </div>
                ) : null}
            </DragOverlay>
        </DndContext>
    );
};

export default QueryBuilder;
