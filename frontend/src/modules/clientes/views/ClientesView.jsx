import React, { useEffect, useState } from 'react';
import {
  Users,
  ShoppingBag,
  TrendingUp,
  Lightbulb,
  Sparkles,
  Percent,
  Search,
  BookOpen
} from 'lucide-react';
import { Doughnut, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';

import RequirePremium from 'shared/components/RequirePremium';
import api from 'core/services/api';
import AppView from 'shared/widgets/AppView/AppView';
import StatCard from 'shared/widgets/StatCard/StatCard';
import DataTable from 'shared/widgets/DataTable/DataTable';
import Badge from 'shared/components/Badge/Badge';
import Spinner from 'shared/components/Spinner/Spinner';
import Alert from 'shared/components/Alert/Alert';

import styles from './ClientesView.module.css';

// Registrar elementos de Chart.js
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

export default function ClientesView() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const getThemeColor = (variableName, fallback) => {
    if (typeof window === 'undefined') return fallback;
    const color = window.getComputedStyle(document.documentElement).getPropertyValue(variableName).trim();
    return color || fallback;
  };

  useEffect(() => {
    const fetchBehaviorData = async () => {
      try {
        const response = await api.get('/reportes/comportamiento-clientes/');
        setData(response.data);
      } catch (err) {
        setError({
          message: err.response?.data?.error || err.response?.data?.detail || "Error al cargar el análisis de comportamiento de clientes.",
          status: err.response?.status
        });
      } finally {
        setLoading(false);
      }
    };
    fetchBehaviorData();
  }, []);

  if (loading) {
    return (
      <AppView title="Clientes" subtitle="Análisis de comportamiento.">
        <div style={{ display: 'flex', justifyContent: 'center', padding: '100px 0' }}>
          <Spinner size="lg" />
        </div>
      </AppView>
    );
  }

  if (error) {
    if (error.status === 403) {
      return (
        <AppView title="Clientes" subtitle="Análisis de comportamiento.">
          <RequirePremium 
            locked={true} 
            title="Análisis de Comportamiento" 
            message="El análisis de comportamiento de clientes es una característica Premium. Mejora tu plan para descubrir quiénes son tus mejores clientes y quiénes están en riesgo."
          >
            <div style={{ height: '600px', display: 'flex', gap: '20px', flexDirection: 'column' }}>
               <div style={{ height: '200px', background: 'var(--color-surface)', borderRadius: '12px' }}></div>
               <div style={{ height: '300px', background: 'var(--color-surface)', borderRadius: '12px' }}></div>
            </div>
          </RequirePremium>
        </AppView>
      );
    }
    return (
      <AppView title="Clientes" subtitle="Análisis de comportamiento.">
        <Alert variant="danger">{error.message}</Alert>
      </AppView>
    );
  }

  const {
    tasa_repeticion,
    total_compradores,
    compradores_recurrentes,
    clientes = [],
    categorias = [],
    reglas = []
  } = data || {};

  // 1. Calcular datos del gráfico Doughnut (Distribución de Segmentos)
  const segmentLabels = ["VIP / Campeón", "Fiel / Frecuente", "Prometedor / Nuevo", "En Riesgo / Inactivo", "Sin Compras"];
  const segmentCounts = segmentLabels.reduce((acc, label) => ({ ...acc, [label]: 0 }), {});

  clientes.forEach(c => {
    const seg = c.segmento || "Sin Compras";
    if (segmentCounts[seg] !== undefined) {
      segmentCounts[seg]++;
    }
  });

  const doughnutData = {
    labels: segmentLabels,
    datasets: [
      {
        data: segmentLabels.map(label => segmentCounts[label]),
        backgroundColor: [
          '#10b981', // VIP: Emerald Green
          '#3b82f6', // Fiel: Blue
          '#06b6d4', // Prometedor: Cyan
          '#f59e0b', // En Riesgo: Amber
          '#64748b', // Sin Compras: Slate
        ],
        borderWidth: 2,
        borderColor: getThemeColor('--color-surface', '#ffffff'),
      }
    ]
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      }
    }
  };

  // 2. Obtener valor máximo de ventas en categorías para escala relativa de barras de progreso
  const maxVentas = categorias.length > 0 ? Math.max(...categorias.map(c => Number(c.total_ventas))) : 1;

  // 3. Calcular Ticket Promedio por Pedido (Monto total dividido entre el número total de pedidos)
  const totalMonetarioSum = clientes.reduce((sum, c) => sum + (c.monetario || 0), 0);
  const totalPedidos = clientes.reduce((sum, c) => sum + (c.frecuencia || 0), 0);
  const ticketPromedio = totalPedidos > 0 ? totalMonetarioSum / totalPedidos : 0;

  // 4. Calcular Ingresos Totales por Segmento para el Gráfico de Barras
  const segmentRevenue = segmentLabels.reduce((acc, label) => ({ ...acc, [label]: 0 }), {});
  clientes.forEach(c => {
    const seg = c.segmento || "Sin Compras";
    if (segmentRevenue[seg] !== undefined) {
      segmentRevenue[seg] += c.monetario || 0;
    }
  });

  const barChartData = {
    labels: ['VIP (Estrella)', 'Fiel (Habitual)', 'Prometedor (Nuevo)', 'Inactivo (En Riesgo)', 'Sin Compras'],
    datasets: [
      {
        label: 'Ingresos Acumulados (Bs.)',
        data: [
          segmentRevenue['VIP / Campeón'] || 0,
          segmentRevenue['Fiel / Frecuente'] || 0,
          segmentRevenue['Prometedor / Nuevo'] || 0,
          segmentRevenue['En Riesgo / Inactivo'] || 0,
          segmentRevenue['Sin Compras'] || 0,
        ],
        backgroundColor: [
          '#10b981', // VIP: Emerald Green
          '#3b82f6', // Fiel: Blue
          '#06b6d4', // Prometedor: Cyan
          '#f59e0b', // En Riesgo: Amber
          '#64748b', // Sin Compras: Slate
        ],
        borderRadius: 6,
        borderWidth: 0,
        barThickness: 45,
      }
    ]
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const val = context.raw || 0;
            return ` Ingresos: Bs. ${Math.round(val).toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: getThemeColor('--color-text-muted', '#94a3b8'),
          font: {
            size: 11,
          }
        }
      },
      y: {
        grid: {
          color: getThemeColor('--color-border', 'rgba(255, 255, 255, 0.05)'),
        },
        ticks: {
          color: getThemeColor('--color-text-muted', '#94a3b8'),
          font: {
            size: 11,
          },
          callback: (value) => `Bs. ${value.toLocaleString()}`,
        }
      }
    }
  };

  // 5. Filtrar clientes por búsqueda (Nombre, Correo o Segmento)
  const filteredClientes = clientes.filter(c =>
    c.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.correo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.segmento || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  // 6. Configurar Columnas de la Tabla RFM
  const getBadgeVariant = (segmento) => {
    switch (segmento) {
      case 'VIP / Campeón': return 'success';
      case 'Fiel / Frecuente': return 'primary';
      case 'Prometedor / Nuevo': return 'info';
      case 'En Riesgo / Inactivo': return 'warning';
      default: return 'default';
    }
  };

  const columns = [
    {
      key: 'nombre', label: 'Cliente', render: (val, row) => (
        <div>
          <div style={{ fontWeight: 600, color: 'var(--color-text, inherit)' }}>{val}</div>
          <div style={{ fontSize: '12px', color: 'var(--color-text-muted, #64748b)' }}>{row.correo}</div>
        </div>
      )
    },
    {
      key: 'recencia',
      label: 'Última Compra (Recencia)',
      align: 'center',
      render: (val) => val !== null ? `Hace ${val} días` : <span style={{ opacity: 0.5 }}>Sin compras</span>
    },
    {
      key: 'frecuencia',
      label: 'Nro. de Pedidos (Frecuencia)',
      align: 'center',
      render: (val) => `${val} pedido${val !== 1 ? 's' : ''}`
    },
    {
      key: 'monetario',
      label: 'Total Gastado (Monto Monetario)',
      align: 'right',
      render: (val) => `Bs. ${Number(val || 0).toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
    },
    {
      key: 'segmento',
      label: 'Segmentación IA (K-Means)',
      align: 'center',
      render: (val) => <Badge variant={getBadgeVariant(val)} dot>{val || 'Sin Compras'}</Badge>
    }
  ];

  return (
    <AppView
      title="Análisis del Comportamiento de Clientes"
      subtitle="Segmentación inteligente e insights de venta cruzada para potenciar tus ventas."
    >
      <div className={styles.container}>

        {/* Top Section Grid: KPIs + Category Preferences */}
        <div className={styles.topSectionGrid} style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <StatCard.Group>
              <StatCard
                label="Total Clientes Registrados"
                value={clientes.length}
                change="Total de usuarios"
                icon={<Users size={24} />}
                accentColor="var(--color-primary)"
              />
              <StatCard
                label="Clientes con Compras (Activos)"
                value={total_compradores}
                change={`${Math.round((total_compradores / (clientes.length || 1)) * 100)}% de conversión de registros`}
                trend="positive"
                icon={<ShoppingBag size={24} />}
                accentColor="#06b6d4"
              />
              <StatCard
                label="Tasa de Retorno (Fidelidad)"
                value={`${tasa_repeticion}%`}
                change={`${compradores_recurrentes} de ${total_compradores} clientes compraron más de una vez`}
                trend="positive"
                icon={<Percent size={24} />}
                accentColor="#10b981"
              />
              <StatCard
                label="Ticket Promedio por Pedido"
                value={`Bs. ${Math.round(ticketPromedio).toLocaleString()}`}
                change="Monto promedio por compra realizada en la app"
                icon={<TrendingUp size={24} />}
                accentColor="#f59e0b"
              />
            </StatCard.Group>
          </div>

          {/* Card: Category Preferences */}
          <div className={styles.card} style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <h3 className={styles.cardTitle} style={{ marginBottom: '15px' }}>
              <TrendingUp size={18} color="#06b6d4" />
              Intereses y Preferencias por Categoría
            </h3>
            {categorias.length > 0 ? (
              <div className={styles.categoryList}>
                {categorias.slice(0, 4).map(cat => {
                  const percent = Math.round((Number(cat.total_ventas) / maxVentas) * 100);
                  return (
                    <div key={cat.producto__categoria__nombre} className={styles.categoryItem}>
                      <div className={styles.categoryHeader}>
                        <span>{cat.producto__categoria__nombre}</span>
                        <span>
                          Bs. {Number(cat.total_ventas).toLocaleString('es-BO', { maximumFractionDigits: 0 })}
                          <span style={{ fontSize: '11px', fontWeight: 'normal', color: 'var(--color-text-muted)', marginLeft: '6px' }}>
                            ({cat.unidades_vendidas} uds)
                          </span>
                        </span>
                      </div>
                      <div className={styles.progressBar}>
                        <div className={styles.progressFill} style={{ width: `${percent}%` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className={styles.emptyState}>
                <BookOpen size={32} />
                <p style={{ marginTop: '10px' }}>No hay ventas registradas en las categorías.</p>
              </div>
            )}
          </div>
        </div>

        {/* Analytics Section: K-Means & Category Preferences */}
        <div className={styles.dashboardGrid}>

          {/* Card: K-Means Segmentation Chart */}
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <Sparkles size={18} color="#3b82f6" />
              Segmentación de Clientes (K-Means)
            </h3>
            <div className={styles.chartSection}>
              <div className={styles.chartContainer}>
                {total_compradores > 0 ? (
                  <Doughnut data={doughnutData} options={doughnutOptions} />
                ) : (
                  <div className={styles.emptyState}>
                    <BookOpen size={32} />
                    <p style={{ marginTop: '10px' }}>No hay suficientes datos de compras para realizar segmentación.</p>
                  </div>
                )}
              </div>
              {total_compradores > 0 && (
                <div className={styles.segmentLegendsGrid}>
                  <div className={styles.legendRow}>
                    <span className={styles.legendDot} style={{ backgroundColor: '#10b981' }} />
                    <div className={styles.legendInfo}>
                      <span className={styles.legendName}>VIP (Clientes Estrella)</span>
                      <span className={styles.legendDesc}>Clientes de alto valor y compras recurrentes en tu app. <strong>Estrategia en el servicio:</strong> Enviar cupones VIP o accesos anticipados a lanzamientos vía correo/notificaciones.</span>
                    </div>
                  </div>
                  <div className={styles.legendRow}>
                    <span className={styles.legendDot} style={{ backgroundColor: '#3b82f6' }} />
                    <div className={styles.legendInfo}>
                      <span className={styles.legendName}>Fiel (Compradores Habituales)</span>
                      <span className={styles.legendDesc}>Clientes leales con visitas frecuentes. <strong>Estrategia en el servicio:</strong> Activar un beneficio en su carrito de compras como envío gratis o puntos extra.</span>
                    </div>
                  </div>
                  <div className={styles.legendRow}>
                    <span className={styles.legendDot} style={{ backgroundColor: '#06b6d4' }} />
                    <div className={styles.legendInfo}>
                      <span className={styles.legendName}>Prometedor (Nuevos con Potencial)</span>
                      <span className={styles.legendDesc}>Compraron recientemente por primera vez. <strong>Estrategia en el servicio:</strong> Enviar por correo sugerencias de productos complementarios a su primera compra.</span>
                    </div>
                  </div>
                  <div className={styles.legendRow}>
                    <span className={styles.legendDot} style={{ backgroundColor: '#f59e0b' }} />
                    <div className={styles.legendInfo}>
                      <span className={styles.legendName}>Inactivo (En Riesgo de Fuga)</span>
                      <span className={styles.legendDesc}>Clientes que no han vuelto a ingresar pedidos. <strong>Estrategia en el servicio:</strong> Enviar campaña con descuento temporal para reactivarlos.</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Card: Revenue per Segment Bar Chart */}
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <TrendingUp size={18} color="#10b981" />
              Ingresos Totales Generados por Segmento (Bs.)
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted, #94a3b8)', marginTop: '-12px', marginBottom: '20px' }}>
              Monto de compras acumulado por tipo de cliente para identificar qué segmento genera mayor rentabilidad.
            </p>
            <div style={{ height: '320px', width: '100%', position: 'relative' }}>
              {total_compradores > 0 ? (
                <Bar data={barChartData} options={barChartOptions} />
              ) : (
                <div className={styles.emptyState}>
                  <BookOpen size={32} />
                  <p style={{ marginTop: '10px' }}>No hay suficientes datos de ventas para mostrar los ingresos por segmento.</p>
                </div>
              )}
            </div>
          </div>

        </div>

        {/* Association Rules Section (Apriori) */}
        <div className={styles.card} style={{ marginBottom: '24px' }}>
          <h3 className={styles.cardTitle}>
            <Lightbulb size={18} color="#10b981" />
            Sugerencias de Venta Cruzada e Inventario (Apriori)
          </h3>
          {reglas.length > 0 ? (
            <div className={styles.rulesList}>
              {reglas.map((r, idx) => (
                <div key={idx} className={styles.ruleCard}>
                  <div className={styles.ruleHeader}>
                    <div className={styles.ruleColumn}>
                      <span className={styles.ruleLabel}>SI EL CLIENTE COMPRA:</span>
                      <span className={styles.tag}>{r.antecedente}</span>
                    </div>

                    <div className={styles.ruleConnector}>
                      <span className={styles.arrowIcon} />
                    </div>

                    <div className={styles.ruleColumn}>
                      <span className={styles.ruleLabelSuccess}>SUGERIR EN CHECKOUT:</span>
                      <span className={styles.tagSuccess}>{r.consecuente}</span>
                    </div>
                  </div>

                  <div className={styles.ruleMeta}>
                    <span className={styles.metaBadge}>
                      Frecuencia de Asociación: <strong>{r.soporte}%</strong>
                    </span>
                    <span className={styles.metaBadge}>
                      Probabilidad de Éxito: <strong>{r.confianza}%</strong>
                    </span>
                  </div>

                  <div className={styles.ruleHint}>
                    💡 <strong>Acción Comercial Recomendada:</strong> Diseñar un pack promocional (combo) ofreciendo ambos artículos con un 5% a 10% de descuento para incentivar la venta complementaria.
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>
              <Lightbulb size={36} style={{ color: 'var(--color-primary, #3b82f6)', marginBottom: '12px' }} />
              <h4 style={{ color: 'var(--color-text, inherit)', fontWeight: '700', fontSize: '15px', marginBottom: '8px' }}>
                ¿Cómo funciona la IA de Recomendaciones?
              </h4>
              <p style={{ maxWidth: '600px', margin: '0 auto 16px auto', fontSize: '13px', lineHeight: '1.5' }}>
                <strong>Apriori</strong> analiza de forma continua el historial de carritos de compras. Cuando detecta que ciertos productos se compran juntos frecuentemente, genera sugerencias automáticas de packs o combos.
              </p>
              <div className={styles.emptyStateTip}>
                <span>💡 Tip para activar:</span> Registra pedidos que contengan múltiples productos en el mismo carrito para que el modelo identifique patrones de asociación y co-ocurrencia.
              </div>
            </div>
          )}
        </div>

        {/* CRM / Clients Data Table */}
        <div className={styles.tableContainer} style={{ marginBottom: '24px' }}>
          <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border, #e2e8f0)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '15px' }}>
              <div>
                <span style={{ fontSize: '16px', fontWeight: 'bold', color: 'var(--color-text, inherit)' }}>
                  Directorio de Clientes y Fichas de Comportamiento (RFM)
                </span>
                <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: 'var(--color-text-muted, #94a3b8)', lineHeight: '1.4' }}>
                  El análisis <strong>RFM</strong> ordena a tus clientes según 3 valores clave:
                  <strong> Recencia</strong> (hace cuánto compró),
                  <strong> Frecuencia</strong> (número de pedidos hechos) y
                  <strong> Valor Monetario</strong> (monto total gastado).
                </p>
              </div>
              <div style={{ position: 'relative', width: '280px' }}>
                <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                <input
                  type="text"
                  placeholder="Buscar por cliente o segmento..."
                  value={searchTerm}
                  onChange={e => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '8px 12px 8px 36px',
                    borderRadius: '8px',
                    border: '1px solid var(--color-border, #e2e8f0)',
                    outline: 'none',
                    fontSize: '14px',
                    backgroundColor: 'var(--color-surface, #ffffff)',
                    color: 'var(--color-text, inherit)'
                  }}
                />
              </div>
            </div>
          </div>
          <DataTable
            columns={columns}
            data={filteredClientes}
            emptyText="No se encontraron clientes que coincidan con la búsqueda."
          />
        </div>

      </div>
    </AppView>
  );
}
