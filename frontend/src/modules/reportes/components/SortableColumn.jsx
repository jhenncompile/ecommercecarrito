import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, X } from 'lucide-react';

const SortableColumn = ({ id, label, onRemove }) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
        zIndex: isDragging ? 10 : 1,
    };

    return (
        <div 
            ref={setNodeRef} 
            style={style}
            className="sortable-column-item"
        >
            <div {...attributes} {...listeners} className="drag-handle">
                <GripVertical size={16} />
            </div>
            <span className="column-label">{label}</span>
            <button className="remove-col-btn" onClick={() => onRemove(id)} type="button">
                <X size={14} />
            </button>
        </div>
    );
};

export default SortableColumn;
