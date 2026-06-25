import styles from './Alert.module.css';
import { CheckCircle2, AlertTriangle, XCircle, Info } from 'lucide-react';

const ICONS = {
  success: CheckCircle2,
  warning: AlertTriangle,
  danger:  XCircle,
  info:    Info,
};

/**
 * Alert — Lego Piece
 * variant: 'success' | 'warning' | 'danger' | 'info'
 */
const Alert = ({ variant = 'info', title, children }) => {
  const Icon = ICONS[variant];
  const cls  = [styles.alert, styles[variant]].filter(Boolean).join(' ');
  return (
    <div className={cls} role="alert">
      {Icon && <Icon size={18} className={styles.icon} />}
      <div>
        {title && <p className={styles.title}>{title}</p>}
        {children && <div className={styles.body}>{children}</div>}
      </div>
    </div>
  );
};

export default Alert;
