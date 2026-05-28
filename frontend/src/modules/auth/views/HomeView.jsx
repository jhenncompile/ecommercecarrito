import { Link } from 'react-router-dom';
import { useState } from 'react';
import { ShoppingCart, BrainCircuit, Box, CreditCard, BarChart3, Package, Layers3, Check, ChevronLeft, ChevronRight } from 'lucide-react';
import styles from './HomeView.module.css';

const features = [
  { icon: ShoppingCart, color: '#e91e63', title: 'Carrito Inteligente',   text: 'Motor de recomendaciones personalizadas que sugiere productos relevantes al cliente.' },
  { icon: BrainCircuit, color: '#6366f1', title: 'Predicción de Ventas IA', text: 'Algoritmos ML analizan tu historial para proyectar demanda futura.' },
  { icon: CreditCard,   color: '#22c55e', title: 'Facturación SIN y QR',  text: 'Integración nativa para pagos QR y emisión automática de facturas.' },
  { icon: BarChart3,    color: '#f97316', title: 'Reportes',              text: 'Dashboard con métricas en tiempo real para analizar tu negocio.' },
  { icon: Package,      color: '#eab308', title: 'Control de Inventario', text: 'Stock en tiempo real, alertas automáticas y manejo de variantes.' },
  { icon: Layers3,      color: '#ef4444', title: 'Arquitectura Headless', text: 'Rápido y adaptable. Tu tienda perfecta en cualquier dispositivo.' },
];

const plans = [
  {
    id: 'basico',
    name: 'Gratuito',
    desc: 'La forma más fácil de empezar. Sin riesgos.',
    price: '0',
    period: 'siempre',
    features: ['Hasta 50 productos', '1 Usuario (Dueño)', 'Punto de venta básico', 'Reportes mensuales'],
    level: 'minimal',
    buttonText: 'Empezar Gratis'
  },
  {
    id: 'profesional',
    name: 'Profesional',
    desc: 'El ecosistema completo para negocios en crecimiento.',
    price: '29',
    period: 'mes',
    features: ['Productos ilimitados', 'Módulo de Inteligencia Artificial', 'Facturación SIN y Pagos QR', 'Reportes en tiempo real', 'Gestión de roles'],
    level: 'pro',
    popular: true,
    buttonText: 'Comenzar Prueba'
  },
  {
    id: 'premium',
    name: 'Premium',
    desc: 'Potencia absoluta y herramientas exclusivas para dominar el mercado.',
    price: '99',
    period: 'mes',
    features: ['Todo lo Profesional', 'Soporte prioritario 24/7', 'Multi-sucursales', 'Auditoría avanzada de acciones', 'SLA garantizado'],
    level: 'premium',
    buttonText: 'Obtener Premium'
  }
];

export default function HomeView() {
  const [activePlanIdx, setActivePlanIdx] = useState(1);

  const nextPlan = () => setActivePlanIdx((p) => (p + 1) % plans.length);
  const prevPlan = () => setActivePlanIdx((p) => (p - 1 + plans.length) % plans.length);

  return (
    <div className={styles.page}>
      {/* NAVBAR */}
      <header className={styles.nav}>
        <div className={styles.brand}>
          <Box size={26} className={styles.brandIcon} />
          <span className={styles.brandName}>MiQhatu</span>
        </div>
        <nav className={styles.navLinks}>
          <a href="#features">Características</a>
          <a href="#pricing">Precios</a>
          <Link to="/login?type=vendedor" className={styles.btnVendedor}>Acceso Vendedor</Link>
          <Link to="/login"        className={styles.btnLogin}>Iniciar Sesión</Link>
          <Link to="/crear-tienda" className={styles.btnRegister}>Crear tienda</Link>
        </nav>
      </header>

      {/* HERO */}
      <section className={styles.hero}>
        <div className={styles.heroBadge}>Nueva plataforma SaaS para emprendedores</div>
        <h1 className={styles.heroTitle}>
          La plataforma e-commerce que <span className={styles.highlight}>piensa por ti</span>, hecho simple.
        </h1>
        <p className={styles.heroSubtitle}>
          Crea tu tienda online en minutos. Carrito inteligente con recomendaciones y predicciones de ventas con IA.
        </p>
        <div className={styles.heroBtns}>
          <Link to="/crear-tienda" className={styles.btnPrimary}>Empezar Gratis</Link>
          <a href="#features"      className={styles.btnSecondary}>Ver características</a>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className={styles.features}>
        <div className={styles.sectionHeader}>
          <h2>Todo lo que tu tienda necesita</h2>
          <p>Herramientas avanzadas de grado empresarial a un precio accesible.</p>
        </div>
        <div className={styles.featuresGrid}>
          {features.map((feat, i) => (
            <div key={i} className={styles.featureCard}>
              <div className={styles.featureIcon} style={{ background: `${feat.color}18`, color: feat.color }}>
                <feat.icon size={22} />
              </div>
              <h3>{feat.title}</h3>
              <p>{feat.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* PRICING CAROUSEL */}
      <section id="pricing" className={styles.pricing}>
        <div className={styles.sectionHeader}>
          <h2>Planes que crecen contigo</h2>
          <p>Comienza gratis y mejora cuando lo necesites. Pagos seguros mediante Stripe.</p>
        </div>
        
        <div className={styles.carouselContainer}>
          <button className={styles.carouselBtn} onClick={prevPlan}>
            <ChevronLeft size={24} />
          </button>
          
          <div className={styles.carouselTrack}>
            {plans.map((plan, idx) => {
              const isActive = idx === activePlanIdx;
              const isPrev = idx === (activePlanIdx - 1 + plans.length) % plans.length;
              const isNext = idx === (activePlanIdx + 1) % plans.length;
              
              let cardClass = styles.priceCard;
              if (isActive) cardClass += ` ${styles.activeCard} ${styles[plan.level]}`;
              else if (isPrev) cardClass += ` ${styles.prevCard} ${styles[plan.level]}`;
              else if (isNext) cardClass += ` ${styles.nextCard} ${styles[plan.level]}`;

              return (
                <div key={plan.id} className={cardClass} onClick={() => setActivePlanIdx(idx)}>
                  {plan.popular && isActive && <div className={styles.popularBadge}>Más Popular</div>}
                  {plan.level === 'premium' && isActive && <div className={styles.premiumBadge}>Máxima Potencia</div>}
                  
                  <h3>{plan.name}</h3>
                  <p>{plan.desc}</p>
                  
                  <div className={styles.price}>
                    ${plan.price} <span>/{plan.period}</span>
                  </div>
                  
                  <ul className={styles.featList}>
                    {plan.features.map((f, i) => (
                      <li key={i}>
                        <Check size={16} className={styles.checkIcon} />
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <Link to={`/crear-tienda?plan=${plan.id}`} className={isActive ? styles.btnCardPrimary : styles.btnCardSecondary}>
                    {plan.buttonText}
                  </Link>
                </div>
              );
            })}
          </div>

          <button className={styles.carouselBtn} onClick={nextPlan}>
            <ChevronRight size={24} />
          </button>
        </div>
        <div className={styles.carouselIndicators}>
          {plans.map((_, idx) => (
            <div 
              key={idx} 
              className={`${styles.indicator} ${idx === activePlanIdx ? styles.indicatorActive : ''}`}
              onClick={() => setActivePlanIdx(idx)}
            />
          ))}
        </div>
      </section>

      <footer className={styles.footer}>
        <p>© 2025 MiQhatu — Todos los derechos reservados.</p>
      </footer>
    </div>
  );
}
