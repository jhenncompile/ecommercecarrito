import styles from './Modal.module.css';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, title, children, footer, zIndex }) {
    if (!isOpen) return null;

    return (
        <div className={styles.overlay} onClick={onClose} style={zIndex ? { zIndex } : undefined}>
            <div className={styles.content} onClick={e => e.stopPropagation()}>
                <div className={styles.header}>
                    <h3 className={styles.title}>{title}</h3>
                    <button className={styles.closeBtn} onClick={onClose}>
                        <X size={20} />
                    </button>
                </div>
                <div className={styles.body}>
                    {children}
                </div>
                {footer && (
                    <div className={styles.footer}>
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
}
