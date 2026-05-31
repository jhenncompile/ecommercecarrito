import React from 'react';
import { Activity, TrendingUp, ArrowDownToLine } from 'lucide-react';
import styles from './DashboardWidgets.module.css';

// ─── FORMATEO INTELIGENTE DE FECHAS ──────────────────────────────────────────
// Detecta si es fecha ISO y la formatea según el tipo de agrupación
const MESES_CORTOS = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];

const fmtLabel = (raw, agruparPor = '') => {
    if (!raw) return 'Sin Agrupar';
    const s = String(raw);
    // Detecta fecha ISO: YYYY-MM-DDTHH... o YYYY-MM-DD
    const matchFull = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (matchFull) {
        const [, year, mm, dd] = matchFull;
        const ag = (agruparPor || '').toLowerCase();
        // Por año: solo mostrar el año
        if (ag.includes('año') || ag.includes('year') || dd === '01' && mm === '01') return year;
        // Por mes: Ene 2023
        if (ag.includes('mes') || ag.includes('month') || dd === '01')
            return `${MESES_CORTOS[parseInt(mm, 10) - 1]} ${year}`;
        // Por día o default: YYYY-MM-DD
        return `${year}-${mm}-${dd}`;
    }
    return s;
};

// Parsea la data del backend, aplicando formateo de fecha inteligente
const parseData = (rawData, agruparPor = '') => {
    if (!rawData || rawData.length === 0) return [];
    return rawData.map(d => ({
        label: fmtLabel(d.grupo ?? d.label, agruparPor),
        value: Number(d.resultado ?? d.value) || 0,
        target: Number(d.target) || 0,
        color: d.color,
        segment1: Number(d.segment1) || 0,
        segment2: Number(d.segment2) || 0,
        segment3: Number(d.segment3) || 0,
        type: d.type
    }));
};

// ─── COMPONENTES DE EJES ─────────────────────────────────────────────────────
const AxisLabel = ({ label, axis }) => {
    if (!label) return null;
    if (axis === 'y') return (
        <div style={{
            position: 'absolute', left: -8, top: '50%',
            transform: 'translateY(-50%) rotate(-90deg)',
            fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-muted)',
            textTransform: 'uppercase', letterSpacing: '0.06em',
            whiteSpace: 'nowrap', pointerEvents: 'none', zIndex: 5,
            maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis'
        }}>{label}</div>
    );
    if (axis === 'x') return (
        <div style={{
            textAlign: 'center', fontSize: '0.62rem', fontWeight: 700,
            color: 'var(--text-muted)', textTransform: 'uppercase',
            letterSpacing: '0.06em', marginTop: '0.25rem', whiteSpace: 'nowrap'
        }}>{label}</div>
    );
    return null;
};

// Líneas de cuadrícula Y para gráficos de barras/línea
const YGridLines = ({ max, steps = 4 }) => {
    const lines = Array.from({ length: steps + 1 }, (_, i) => i / steps);
    const fmt = (v) => {
        const n = v * max;
        if (n >= 1_000_000) return `${(n/1_000_000).toFixed(1)}M`;
        if (n >= 1_000)     return `${(n/1_000).toFixed(0)}K`;
        return Math.round(n).toLocaleString();
    };
    return (
        <>
            {lines.map((pct, i) => (
                <div key={i} style={{
                    position: 'absolute', left: 0, right: 0,
                    bottom: `${pct * 100}%`,
                    borderTop: `1px ${pct === 0 ? 'solid' : 'dashed'} var(--border-color)`,
                    zIndex: 0, pointerEvents: 'none'
                }}>
                    {pct > 0 && (
                        <span style={{
                            position: 'absolute', right: 'calc(100% + 4px)', top: '-9px',
                            fontSize: '0.58rem', color: 'var(--text-muted)',
                            fontWeight: 600, whiteSpace: 'nowrap'
                        }}>{fmt(pct)}</span>
                    )}
                </div>
            ))}
        </>
    );
};

// ─── BAR ─────────────────────────────────────────────────────────────────────
export const CustomBarChart = ({ data, yLabel, xLabel, agruparPor }) => {
    const parsed = parseData(data, agruparPor);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const max = Math.max(...parsed.map(d => d.value)) || 1;
    const minW = Math.max(parsed.length * 44, 200);
    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            <div className={styles.chartScrollWrapper}>
                <div style={{ position: 'relative', paddingLeft: yLabel ? 18 : 4, paddingRight: 4, minWidth: minW }}>
                    {yLabel && <AxisLabel label={yLabel} axis="y" />}
                    <div className={styles.chartContainer} style={{ alignItems: 'flex-end', position: 'relative' }}>
                        <YGridLines max={max} />
                        {parsed.map((d, i) => (
                            <div key={i} className={styles.barWrapper}>
                                <div className={styles.bar}
                                    style={{ height: `${(d.value / max) * 100}%`, background: 'linear-gradient(to top, var(--primary), #60a5fa)', zIndex: 1 }}>
                                    <div className={styles.barTooltip}>{d.value.toLocaleString()}</div>
                                </div>
                                <span className={styles.barLabel}>{d.label}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
            {xLabel && <AxisLabel label={xLabel} axis="x" />}
        </div>
    );
};

// ─── LINE ─────────────────────────────────────────────────────────────────────
export const CustomLineChart = ({ data, color = '#10b981', yLabel, xLabel, agruparPor }) => {
    const parsed = parseData(data, agruparPor);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const max = Math.max(...parsed.map(d => d.value)) || 1;
    const points = parsed.map((d, i) => {
        const x = (i / (parsed.length - 1 || 1)) * 100;
        const y = 100 - (d.value / max) * 100;
        return `${x},${y}`;
    }).join(' ');
    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            <div style={{ position: 'relative', paddingLeft: yLabel ? 18 : 4, flex: 1 }}>
                {yLabel && <AxisLabel label={yLabel} axis="y" />}
                <div className={styles.lineChartContainer}>
                    <svg className={styles.lineSvg} preserveAspectRatio="none" viewBox="0 -5 100 110">
                        <defs>
                            <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor={color} stopOpacity="0.3" />
                                <stop offset="100%" stopColor={color} stopOpacity="0" />
                            </linearGradient>
                        </defs>
                        {/* Grid horizontals */}
                        {[25, 50, 75].map(pct => (
                            <line key={pct} x1="0" y1={100 - pct} x2="100" y2={100 - pct}
                                stroke="var(--border-color)" strokeWidth="0.4" strokeDasharray="2,2" />
                        ))}
                        <polygon points={`0,100 ${points} 100,100`} fill="url(#lineGrad)" />
                        <polyline fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" points={points} />
                        {parsed.map((d, i) => {
                            const x = (i / (parsed.length - 1 || 1)) * 100;
                            const y = 100 - (d.value / max) * 100;
                            return <circle key={i} cx={x} cy={y} r="2.5" fill="white" stroke={color} strokeWidth="1.5"><title>{d.label}: {d.value.toLocaleString()}</title></circle>;
                        })}
                    </svg>
                    <div className={styles.lineLabels}>
                        {parsed.map((d, i) => <span key={i} className={styles.barLabel}>{d.label}</span>)}
                    </div>
                </div>
            </div>
            {xLabel && <AxisLabel label={xLabel} axis="x" />}
        </div>
    );
};

// ─── PIE ─────────────────────────────────────────────────────────────────────
export const CustomPieChart = ({ data }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const total = parsed.reduce((a, d) => a + d.value, 0) || 1;
    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
    let cum = 0;
    const items = parsed.map((d, i) => {
        const pct = (d.value / total) * 100;
        const color = d.color || COLORS[i % COLORS.length];
        const r = { ...d, pct, color, start: cum };
        cum += pct;
        return r;
    });
    const gradient = items.map(d => `${d.color} ${d.start}% ${d.start + d.pct}%`).join(', ');
    return (
        <div className={styles.pieContainer}>
            <div className={styles.pieCircle} style={{ background: `conic-gradient(${gradient})` }} />
            <div className={styles.pieLegend}>
                {items.map((d, i) => (
                    <div key={i} className={styles.pieLegendItem}>
                        <div className={styles.pieColorDot} style={{ backgroundColor: d.color }} />
                        <div>
                            <p className={styles.pieLegendLabel}>{d.label}</p>
                            <p className={styles.pieLegendValue}>{d.value.toLocaleString()} ({Math.round(d.pct)}%)</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// ─── DOUGHNUT ─────────────────────────────────────────────────────────────────
export const CustomDoughnutChart = ({ data }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const total = parsed.reduce((a, d) => a + d.value, 0) || 1;
    const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];
    let cum = 0;
    const items = parsed.map((d, i) => {
        const pct = (d.value / total) * 100;
        const color = d.color || COLORS[i % COLORS.length];
        const r = { ...d, pct, color, start: cum };
        cum += pct;
        return r;
    });
    const gradient = items.map(d => `${d.color} ${d.start}% ${d.start + d.pct}%`).join(', ');
    return (
        <div className={styles.pieContainer}>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div className={styles.pieCircle} style={{ background: `conic-gradient(${gradient})`, width: 140, height: 140 }} />
                <div style={{
                    position: 'absolute', width: 76, height: 76, background: 'var(--bg-card)',
                    borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 900, fontSize: '1rem', color: 'var(--text-main)'
                }}>{total.toLocaleString()}</div>
            </div>
            <div className={styles.pieLegend}>
                {items.map((d, i) => (
                    <div key={i} className={styles.pieLegendItem}>
                        <div className={styles.pieColorDot} style={{ backgroundColor: d.color }} />
                        <div>
                            <p className={styles.pieLegendLabel}>{d.label}</p>
                            <p className={styles.pieLegendValue}>{d.value.toLocaleString()} — {Math.round(d.pct)}%</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// ─── KPI ─────────────────────────────────────────────────────────────────────
export const KPICard = ({ title, data }) => {
    const parsed = parseData(data);
    const value = parsed.reduce((a, d) => a + d.value, 0);
    return (
        <div className={styles.kpiContainer}>
            <div className={styles.kpiTrend}>
                <Activity size={14} />
                <span style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>{title || 'Métrica'}</span>
            </div>
            <p className={styles.kpiValue}>{value.toLocaleString()}</p>
        </div>
    );
};

// ─── TABLE ─────────────────────────────────────────────────────────────────────
export const CustomTable = ({ data, columns, xLabel, yLabel }) => {
    if (!data || !data.length) return <div className={styles.empty}>Sin datos</div>;
    const colKeys = columns?.length ? columns : Object.keys(data[0]);

    // Renombrar columnas con los labels si los hay
    const colHeaders = colKeys.map(k => {
        if (xLabel && (k === 'grupo' || k === 'label')) return xLabel;
        if (yLabel && (k === 'resultado' || k === 'value')) return yLabel;
        return k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    });

    return (
        <div className={styles.tableContainer}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        {colHeaders.map((h, i) => <th key={i}>{h}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, i) => (
                        <tr key={i}>
                            {colKeys.map((k, j) => {
                                let val = row[k] ?? '';
                                // Formatear fechas en celdas también
                                if (typeof val === 'string' && /^\d{4}-\d{2}-\d{2}[T ]/.test(val)) {
                                    val = val.slice(0, 10);
                                }
                                return <td key={k}>{String(val)}</td>;
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// ─── WATERFALL ─────────────────────────────────────────────────────────────────
export const CustomWaterfallChart = ({ data, yLabel, xLabel }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const max = Math.max(...parsed.map(d => Math.abs(d.value))) * 1.2 || 1;
    let running = 0;
    const barColors = { positive: '#10b981', negative: '#f43f5e', total: '#475569' };
    const minW = Math.max(parsed.length * 52, 220);
    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            <div className={styles.chartScrollWrapper}>
                <div style={{ position: 'relative', paddingLeft: yLabel ? 20 : 4, minWidth: minW }}>
                    {yLabel && <AxisLabel label={yLabel} axis="y" />}
                    <div className={styles.chartContainer} style={{ alignItems: 'flex-end', minHeight: '13rem', position: 'relative' }}>
                        <YGridLines max={max} steps={3} />
                        {parsed.map((d, i) => {
                            let startY, endY;
                            if (d.type === 'total') { startY = 0; endY = d.value; }
                            else { startY = running; endY = running + d.value; running = endY; }
                            const h = (Math.abs(d.value) / max) * 100;
                            const bot = (Math.min(startY, endY) / max) * 100;
                            return (
                                <div key={i} className={styles.barWrapper} style={{ position: 'relative' }}>
                                    <div style={{
                                        width: '100%', position: 'absolute',
                                        height: `${h}%`, bottom: `${bot}%`,
                                        background: barColors[d.type] || barColors.positive,
                                        borderRadius: 4, transition: 'all 0.4s', zIndex: 1
                                    }}>
                                        <div className={styles.barTooltip}>{d.type === 'negative' ? '-' : ''}${Math.abs(d.value).toLocaleString()}</div>
                                    </div>
                                    <span className={styles.barLabel} style={{ position: 'absolute', bottom: '-20px' }}>{d.label}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
            {xLabel && <AxisLabel label={xLabel} axis="x" />}
        </div>
    );
};

// ─── COHORT ─────────────────────────────────────────────────────────────────
export const CustomCohortAnalysis = ({ data }) => {
    if (!data?.length) return <div className={styles.empty}>Sin datos</div>;
    return (
        <div className={styles.tableContainer}>
            <table className={styles.table} style={{ textAlign: 'center' }}>
                <thead>
                    <tr>
                        <th style={{ textAlign: 'left' }}>Cohorte</th>
                        {data[0].data?.map((_, i) => <th key={i}>Mes {i}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, i) => (
                        <tr key={i}>
                            <td style={{ textAlign: 'left', fontWeight: 700 }}>{row.cohort || row.label}</td>
                            {row.data?.map((val, j) => (
                                <td key={j} style={{ padding: '0.25rem' }}>
                                    <div style={{
                                        width: '100%', padding: '0.4rem', borderRadius: 6, fontWeight: 700, fontSize: '0.78rem',
                                        background: `rgba(59,130,246,${Math.max(0.1, val / 100)})`,
                                        color: val > 40 ? 'white' : 'var(--text-main)'
                                    }}>{val}%</div>
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

// ─── HEATMAP ─────────────────────────────────────────────────────────────────
export const CustomHeatmap = ({ data }) => {
    if (!data?.matrix) return <div className={styles.empty}>Sin datos</div>;
    const { days, times, matrix } = data;
    const maxVal = Math.max(...matrix.map(d => d.value)) || 1;
    return (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '0.25rem', padding: '0.25rem 0' }}>
            <div style={{ display: 'flex', paddingLeft: '3.5rem', gap: '0.25rem' }}>
                {times?.map(t => <div key={t} style={{ flex: 1, textAlign: 'center', fontSize: '0.65rem', fontWeight: 700, color: 'var(--text-muted)' }}>{t}</div>)}
            </div>
            {days?.map(day => (
                <div key={day} style={{ display: 'flex', gap: '0.25rem', alignItems: 'center' }}>
                    <span style={{ width: '3.5rem', fontSize: '0.68rem', fontWeight: 700, color: 'var(--text-muted)', textAlign: 'right', paddingRight: '0.5rem', flexShrink: 0 }}>{day}</span>
                    {times?.map(time => {
                        const cell = matrix.find(m => m.day === day && m.time === time);
                        const opacity = cell ? Math.max(0.05, cell.value / maxVal) : 0;
                        return (
                            <div key={time} title={`${day} ${time}: ${cell?.value || 0} ventas`}
                                style={{ flex: 1, height: '1.8rem', borderRadius: 4, background: `rgba(16,185,129,${opacity})`, cursor: 'pointer', transition: 'all 0.2s' }} />
                        );
                    })}
                </div>
            ))}
            <div style={{ textAlign: 'center', fontSize: '0.62rem', color: 'var(--text-muted)', marginTop: '0.25rem', fontWeight: 600 }}>Intensidad de actividad por hora y día</div>
        </div>
    );
};

// ─── RADAR ─────────────────────────────────────────────────────────────────
export const CustomRadarChart = ({ data }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const size = 200, center = 100, radius = 80;
    const max = Math.max(...parsed.map(d => d.value)) || 100;
    const coords = (val, idx, total) => {
        const angle = (Math.PI * 2 * idx) / total - Math.PI / 2;
        const r = (val / max) * radius;
        return { x: center + r * Math.cos(angle), y: center + r * Math.sin(angle) };
    };
    const pts = parsed.map((d, i) => coords(d.value, i, parsed.length));
    const poly = pts.map(p => `${p.x},${p.y}`).join(' ');
    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%', minHeight: '14rem' }}>
            <svg viewBox={`0 0 ${size} ${size}`} width="100%" style={{ maxWidth: 240, overflow: 'visible' }}>
                {[20, 40, 60, 80, 100].map(level => {
                    const lp = parsed.map((_, i) => coords((level / 100) * max, i, parsed.length));
                    return <polygon key={level} points={lp.map(p => `${p.x},${p.y}`).join(' ')} fill="none" stroke="var(--border-color)" strokeWidth="0.8" />;
                })}
                {parsed.map((_, i) => {
                    const end = coords(max, i, parsed.length);
                    return <line key={i} x1={center} y1={center} x2={end.x} y2={end.y} stroke="var(--border-color)" strokeWidth="0.8" />;
                })}
                <polygon points={poly} fill="rgba(139,92,246,0.25)" stroke="#8b5cf6" strokeWidth="2" />
                {parsed.map((d, i) => {
                    const p = coords(d.value, i, parsed.length);
                    const lp = coords(max * 1.28, i, parsed.length);
                    return (
                        <g key={i}>
                            <circle cx={p.x} cy={p.y} r="3" fill="#8b5cf6"><title>{d.label}: {d.value}</title></circle>
                            <text x={lp.x} y={lp.y} textAnchor="middle" dominantBaseline="middle" fontSize="8" fill="var(--text-muted)" fontWeight="700">{d.label}</text>
                        </g>
                    );
                })}
            </svg>
        </div>
    );
};

// ─── SPARKLINE KPI ─────────────────────────────────────────────────────────────
export const SparklineKPI = ({ title, value, trend, trendData, isNegativeGood = false }) => {
    const arr = trendData || [0];
    const max = Math.max(...arr), min = Math.min(...arr), range = max - min || 1;
    const pts = arr.map((v, i) => `${(i / (arr.length - 1 || 1)) * 100},${100 - ((v - min) / range) * 80 - 10}`).join(' ');
    const isPos = trend >= 0;
    const isGood = isNegativeGood ? !isPos : isPos;
    const col = isGood ? '#10b981' : '#f43f5e';
    const bgCol = isGood ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)';
    return (
        <div className={styles.kpiContainer} style={{ position: 'relative', overflow: 'hidden', minHeight: '9rem' }}>
            <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', height: '60px', opacity: 0.3 }}>
                <svg preserveAspectRatio="none" viewBox="0 0 100 100" style={{ width: '100%', height: '100%' }}>
                    <polyline fill="none" stroke={col} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" points={pts} />
                </svg>
            </div>
            <div style={{ position: 'relative', zIndex: 1 }}>
                <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-muted)' }}>{title}</span>
                <p className={styles.kpiValue}>{value}</p>
                <div className={styles.kpiTrend} style={{ color: col }}>
                    {isPos ? <TrendingUp size={12} /> : <ArrowDownToLine size={12} />}
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, background: bgCol, padding: '2px 8px', borderRadius: 6 }}>
                        {Math.abs(trend)}% vs Ant.
                    </span>
                </div>
            </div>
        </div>
    );
};

// ─── HORIZONTAL BAR ─────────────────────────────────────────────────────────────
export const CustomHorizontalBarChart = ({ data, xLabel, yLabel }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const sorted = [...parsed].sort((a, b) => b.value - a.value).slice(0, 10);
    const max = Math.max(...sorted.map(d => d.value)) || 1;
    const fmt = (n) => n >= 1000 ? `${(n/1000).toFixed(1)}K` : n.toLocaleString();
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem', width: '100%', height: '100%' }}>
            {/* Cabecera de columnas */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', paddingBottom: '0.35rem', borderBottom: '1px solid var(--border-color)', marginBottom: '0.25rem' }}>
                <span style={{ width: '5.5rem', flexShrink: 0, fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', textAlign: 'right' }}>
                    {xLabel || 'Categoría'}
                </span>
                <span style={{ flex: 1, fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                    {yLabel || 'Valor'}
                </span>
            </div>
            {sorted.map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{
                        width: '5.5rem', fontSize: '0.72rem', fontWeight: 700,
                        color: 'var(--text-muted)', textAlign: 'right', flexShrink: 0,
                        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
                    }} title={d.label}>{d.label}</span>
                    <div style={{ flex: 1, background: 'var(--bg-body)', borderRadius: 5, height: '1.6rem', overflow: 'hidden', position: 'relative' }}>
                        <div style={{
                            width: `${(d.value / max) * 100}%`, height: '100%',
                            background: `linear-gradient(to right, var(--primary), #60a5fa)`,
                            borderRadius: 5, transition: 'width 0.5s'
                        }} />
                        <span style={{
                            position: 'absolute', right: '0.5rem', top: '50%', transform: 'translateY(-50%)',
                            fontSize: '0.68rem', fontWeight: 800, color: 'var(--text-main)'
                        }}>{fmt(d.value)}</span>
                    </div>
                </div>
            ))}
        </div>
    );
};

// ─── STACKED BAR ─────────────────────────────────────────────────────────────────
export const CustomStackedBarChart = ({ data, yLabel, xLabel }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const max = Math.max(...parsed.map(d => (d.segment1 + d.segment2 + d.segment3))) || 1;
    const minW = Math.max(parsed.length * 48, 200);
    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            {/* Leyenda de segmentos */}
            <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                {[['#3b82f6','Segmento 1'],['#6366f1','Segmento 2'],['#8b5cf6','Segmento 3']].map(([col, lbl]) => (
                    <span key={lbl} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.65rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                        <span style={{ width: 10, height: 10, borderRadius: 2, background: col, flexShrink: 0 }} />{lbl}
                    </span>
                ))}
            </div>
            <div className={styles.chartScrollWrapper}>
                <div style={{ position: 'relative', paddingLeft: yLabel ? 18 : 4, minWidth: minW }}>
                    {yLabel && <AxisLabel label={yLabel} axis="y" />}
                    <div className={styles.chartContainer} style={{ alignItems: 'flex-end', position: 'relative' }}>
                        <YGridLines max={max} steps={3} />
                        {parsed.map((d, i) => {
                            const total = d.segment1 + d.segment2 + d.segment3;
                            return (
                                <div key={i} className={styles.barWrapper}>
                                    <div style={{ width: '100%', height: `${(total / max) * 100}%`, display: 'flex', flexDirection: 'column-reverse', borderRadius: '4px 4px 0 0', overflow: 'hidden', zIndex: 1 }}>
                                        <div style={{ width: '100%', height: `${(d.segment1 / (total || 1)) * 100}%`, background: '#3b82f6' }} title={`S1: ${d.segment1}`} />
                                        <div style={{ width: '100%', height: `${(d.segment2 / (total || 1)) * 100}%`, background: '#6366f1' }} title={`S2: ${d.segment2}`} />
                                        <div style={{ width: '100%', height: `${(d.segment3 / (total || 1)) * 100}%`, background: '#8b5cf6' }} title={`S3: ${d.segment3}`} />
                                    </div>
                                    <span className={styles.barLabel}>{d.label}</span>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
            {xLabel && <AxisLabel label={xLabel} axis="x" />}
        </div>
    );
};

// ─── FUNNEL ─────────────────────────────────────────────────────────────────
export const CustomFunnelChart = ({ data, yLabel }) => {
    const parsed = parseData(data);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const max = parsed[0]?.value || 1;
    const COLORS = ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#1d4ed8'];
    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.3rem', padding: '0.5rem 0', width: '100%' }}>
            {yLabel && <div style={{ fontSize: '0.62rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>{yLabel}</div>}
            {parsed.map((d, i) => {
                const widthPct = (d.value / max) * 100;
                const convPct = i > 0 ? ((d.value / parsed[i-1].value) * 100).toFixed(0) : null;
                return (
                    <div key={i} style={{ width: `${widthPct}%`, display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
                        <div style={{
                            width: '100%', height: '2.2rem', background: d.color || COLORS[i % COLORS.length],
                            borderRadius: 4, display: 'flex', alignItems: 'center', justifyContent: 'center',
                            clipPath: 'polygon(1% 0, 99% 0, 100% 100%, 0% 100%)', transition: 'all 0.4s'
                        }}>
                            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'white' }}>{d.value.toLocaleString()}</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.1rem' }}>
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>{d.label}</span>
                            {convPct && <span style={{ fontSize: '0.62rem', background: 'rgba(16,185,129,0.12)', color: '#059669', padding: '1px 5px', borderRadius: 4, fontWeight: 700 }}>{convPct}%</span>}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

// ─── AREA ─────────────────────────────────────────────────────────────────
export const CustomAreaChart = ({ data, color = '#10b981', yLabel, xLabel, agruparPor }) => {
    const parsed = parseData(data, agruparPor);
    if (!parsed.length) return <div className={styles.empty}>Sin datos</div>;
    const max = Math.max(...parsed.map(d => d.value)) || 1;
    const pts = parsed.map((d, i) => `${(i / (parsed.length - 1 || 1)) * 100},${100 - (d.value / max) * 100}`);
    return (
        <div style={{ display: 'flex', flexDirection: 'column', width: '100%', height: '100%' }}>
            <div style={{ position: 'relative', paddingLeft: yLabel ? 18 : 4, flex: 1 }}>
                {yLabel && <AxisLabel label={yLabel} axis="y" />}
                <div className={styles.lineChartContainer}>
                    <svg className={styles.lineSvg} preserveAspectRatio="none" viewBox="0 0 100 100">
                        <defs>
                            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="0%" stopColor={color} stopOpacity="0.35" />
                                <stop offset="100%" stopColor={color} stopOpacity="0" />
                            </linearGradient>
                        </defs>
                        {[25, 50, 75].map(pct => (
                            <line key={pct} x1="0" y1={pct} x2="100" y2={pct}
                                stroke="var(--border-color)" strokeWidth="0.4" strokeDasharray="2,2" />
                        ))}
                        <polygon points={`0,100 ${pts.join(' ')} 100,100`} fill="url(#areaGrad)" />
                        <polyline fill="none" stroke={color} strokeWidth="2.5" points={pts.join(' ')} />
                    </svg>
                    <div className={styles.lineLabels}>
                        {parsed.map((d, i) => <span key={i} className={styles.barLabel}>{d.label}</span>)}
                    </div>
                </div>
            </div>
            {xLabel && <AxisLabel label={xLabel} axis="x" />}
        </div>
    );
};
