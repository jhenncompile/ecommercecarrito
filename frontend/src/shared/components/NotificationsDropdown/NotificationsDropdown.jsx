import React, { useState, useEffect, useRef } from 'react';
import { Bell, Check } from 'lucide-react';
import api from 'core/services/api';
import { isBaseDomain } from 'core/utils/domain';
import styles from './NotificationsDropdown.module.css';

const NotificationsDropdown = () => {
    const [open, setOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [loading, setLoading] = useState(false);
    const dropdownRef = useRef(null);
    const intervalRef = useRef(null);

    // En dominio base (localhost / public schema) no hay notificaciones de tenant
    const isBase = isBaseDomain(window.location.hostname);

    const fetchNotifications = async () => {
        // Solo buscar notificaciones en contexto de tenant y si hay token
        if (isBase) return;
        const token = localStorage.getItem('access_token');
        if (!token) {
            if (intervalRef.current) clearInterval(intervalRef.current);
            return;
        }

        try {
            setLoading(true);
            const res = await api.get('/notificaciones/');
            const data = Array.isArray(res.data) ? res.data : res.data.results || [];
            setNotifications(data);
            setUnreadCount(data.filter(n => !n.leido).length);
        } catch (error) {
            // Si es 401 o error de red, el token es inválido o el backend no responde, detenemos el polling
            if (error.response?.status === 401 || error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
                if (intervalRef.current) {
                    clearInterval(intervalRef.current);
                    intervalRef.current = null;
                }
            } else {
                // Solo logueamos otros errores si no son de red puros para no inundar la consola
                console.error('Error fetching notifications', error);
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isBase) return; // no montar polling en dominio base
        fetchNotifications();
        intervalRef.current = setInterval(fetchNotifications, 30000);
        return () => {
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const markAsRead = async (id) => {
        try {
            await api.patch(`/notificaciones/${id}/`, { leido: true });
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, leido: true } : n));
            setUnreadCount(prev => Math.max(0, prev - 1));
        } catch (e) {
            console.error(e);
        }
    };

    const markAllAsRead = async () => {
        try {
            await api.post('/notificaciones/marcar-todas-leidas/');
            setNotifications(prev => prev.map(n => ({ ...n, leido: true })));
            setUnreadCount(0);
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className={styles.dropdownContainer} ref={dropdownRef}>
            <div className={styles.iconBtn} onClick={() => setOpen(!open)}>
                <Bell size={20} />
                {unreadCount > 0 && (
                    <span className={styles.badge}>{unreadCount}</span>
                )}
            </div>

            {open && (
                <div className={styles.dropdownMenu}>
                    <div className={styles.header}>
                        <h3>Notificaciones</h3>
                        {unreadCount > 0 && (
                            <button onClick={markAllAsRead} className={styles.markAllBtn}>
                                <Check size={14} /> Marcar todo como leído
                            </button>
                        )}
                    </div>
                    
                    <div className={styles.list}>
                        {loading && notifications.length === 0 ? (
                            <div className={styles.empty}>Cargando...</div>
                        ) : notifications.length === 0 ? (
                            <div className={styles.empty}>No tienes notificaciones</div>
                        ) : (
                            notifications.map(notif => (
                                <div 
                                    key={notif.id} 
                                    className={`${styles.item} ${!notif.leido ? styles.unread : ''}`}
                                    onClick={() => !notif.leido && markAsRead(notif.id)}
                                >
                                    <div className={styles.itemHeader}>
                                        <span className={styles.title}>{notif.titulo}</span>
                                        <span className={styles.time}>
                                            {new Date(notif.fecha_creacion).toLocaleDateString()}
                                        </span>
                                    </div>
                                    <p className={styles.message}>{notif.mensaje}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default NotificationsDropdown;
