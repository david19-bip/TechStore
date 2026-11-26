import { money, pretty } from '../../lib/api'
import type { User } from '../../lib/api'
import heroArt from '../../assets/techstore-hero.jpg'

type Row = Record<string, unknown>
type PageKey = 'dashboard' | 'productos' | 'categorias' | 'clientes' | 'proveedores' | 'ventas' | 'compras' | 'inventario' | 'alertas' | 'reportes' | 'usuarios' | 'auditoria'
const rolesLabel: Record<string, string> = { administrador: 'Administrador', vendedor: 'Vendedor', bodeguero: 'Bodeguero' }

const dashboardLabels: Record<string, string> = {
  categorias_activas: 'Categorías activas', productos_activos: 'Productos activos', productos_bajo_stock: 'Alertas de stock', unidades_en_inventario: 'Unidades en inventario', proveedores_activos: 'Proveedores activos', clientes_activos: 'Clientes activos', total_compras_registradas: 'Compras registradas', valor_total_compras: 'Valor de compras', total_ventas_registradas: 'Ventas registradas', ingresos_totales_ventas: 'Ingresos por ventas', costo_productos_vendidos: 'Costo vendido', utilidad_bruta: 'Utilidad bruta',
}


export default function DashboardView({ data, loading, onNavigate, role }: { data: Row | null; loading: boolean; onNavigate: (key: PageKey) => void; role: User['rol'] }) {
  const quickActions: { key: PageKey; label: string; help: string; icon: string; color: string }[] = [
    ...(role !== 'bodeguero' ? [{ key: 'ventas' as PageKey, label: 'Nueva venta', help: 'Registrar una venta', icon: '↗', color: 'green' }] : []),
    ...(role !== 'vendedor' ? [{ key: 'compras' as PageKey, label: 'Nueva compra', help: 'Ingresar mercancía', icon: '↙', color: 'blue' }] : []),
    { key: 'productos', label: 'Productos', help: 'Consultar catálogo', icon: '▦', color: 'purple' },
    { key: 'alertas', label: 'Stock bajo', help: 'Ver productos por reponer', icon: '!', color: 'orange' },
    ...(role === 'vendedor' ? [{ key: 'clientes' as PageKey, label: 'Clientes', help: 'Consultar clientes', icon: '♙', color: 'blue' }] : []),
    ...(role === 'bodeguero' ? [{ key: 'proveedores' as PageKey, label: 'Proveedores', help: 'Consultar proveedores', icon: '▤', color: 'blue' }] : []),
    ...(role !== 'vendedor' ? [{ key: 'inventario' as PageKey, label: 'Kardex', help: 'Ver movimientos', icon: '◉', color: 'orange' }] : []),
  ]
  const metricKeys = role === 'vendedor'
    ? ['productos_activos', 'productos_bajo_stock', 'clientes_activos', 'total_ventas_registradas']
    : role === 'bodeguero'
      ? ['unidades_en_inventario', 'productos_bajo_stock', 'proveedores_activos', 'total_compras_registradas']
      : ['ingresos_totales_ventas', 'productos_activos', 'productos_bajo_stock', 'utilidad_bruta']
  const metricIcon: Record<string, string> = { ingresos_totales_ventas: '↗', productos_activos: '▦', productos_bajo_stock: '!', utilidad_bruta: '◈', total_ventas_registradas: '▧', clientes_activos: '♙', unidades_en_inventario: '◉', total_compras_registradas: '↙', valor_total_compras: '$', proveedores_activos: '▤' }
  const captions: Record<string, string> = { ingresos_totales_ventas: 'Ingresos acumulados', productos_activos: 'En catálogo activo', productos_bajo_stock: 'Requieren reposición', utilidad_bruta: 'Ingresos menos costo vendido', total_ventas_registradas: 'Transacciones registradas', clientes_activos: 'Clientes disponibles', unidades_en_inventario: 'Unidades disponibles', total_compras_registradas: 'Órdenes registradas', valor_total_compras: 'Valor de órdenes recibidas', proveedores_activos: 'Proveedores disponibles' }
  const isMoney = (key: string) => ['ingresos_totales_ventas', 'utilidad_bruta', 'valor_total_compras'].includes(key)
  const heading = role === 'vendedor' ? 'Panel de ventas' : role === 'bodeguero' ? 'Panel de inventario' : 'Resumen general'
  const description = role === 'vendedor' ? 'Consulta clientes, registra ventas y revisa el catálogo.' : role === 'bodeguero' ? 'Controla existencias, compras y movimientos de bodega.' : 'Indicadores y actividad general de TechStore.'
  const healthSource: [string, unknown, string][] = role === 'vendedor'
    ? [['Ventas registradas', data?.total_ventas_registradas, '↗'], ['Clientes activos', data?.clientes_activos, '♙'], ['Productos activos', data?.productos_activos, '▦'], ['Alertas de stock', data?.productos_bajo_stock, '!']]
    : role === 'bodeguero'
      ? [['Unidades en inventario', data?.unidades_en_inventario, '▦'], ['Productos con stock bajo', data?.productos_bajo_stock, '!'], ['Proveedores activos', data?.proveedores_activos, '▤'], ['Compras registradas', data?.total_compras_registradas, '↙']]
      : [['Unidades en inventario', data?.unidades_en_inventario, '▦'], ['Categorías activas', data?.categorias_activas, '◈'], ['Clientes activos', data?.clientes_activos, '♙'], ['Proveedores activos', data?.proveedores_activos, '▤']]
  const healthRows = healthSource.map(([label, value, icon]) => ({ label, value, icon }))
  return <div className="dashboard-page"><div className="page-heading"><div><div className="eyebrow">{rolesLabel[role].toUpperCase()}</div><h1>{heading} <span className="wave">✦</span></h1><p className="muted">{description}</p></div>{role === 'administrador' && <button className="button secondary" onClick={() => onNavigate('reportes')}>Ver reportes <span>↗</span></button>}</div>
    <section className="store-hero" style={{ backgroundImage: `linear-gradient(90deg, rgba(10,28,44,.98) 0%, rgba(10,28,44,.91) 34%, rgba(10,28,44,.34) 62%, rgba(10,28,44,.05) 100%), url(${heroArt})` }}><div className="hero-copy"><div className="hero-kicker"><span className="hero-spark">✦</span> TECNOLOGÍA PARA IR MÁS LEJOS</div><h2>Equipos que impulsan<br/>el próximo nivel.</h2><p>Tu catálogo tecnológico, inventario y ventas bajo control.</p><div className="hero-actions"><button className="hero-button" onClick={() => onNavigate('productos')}>Explorar catálogo <span>↗</span></button><span className="hero-note"><i/> Stock y operación en tiempo real</span></div></div><div className="hero-orbit orbit-a"/><div className="hero-orbit orbit-b"/></section>
    <div className="metric-grid">{metricKeys.map((key, i) => <article className={`metric-card metric-${i}`} key={key}><div className="metric-top"><span>{dashboardLabels[key]}</span><span className="metric-icon">{metricIcon[key]}</span></div><strong>{loading ? '…' : isMoney(key) ? money(data?.[key]) : pretty(data?.[key])}</strong><small>{captions[key]}</small></article>)}</div>
    <div className="dashboard-grid"><section className="panel activity-panel"><div className="panel-heading"><div><span className="eyebrow">OPERACIÓN</span><h2>Accesos rápidos</h2></div><span className="subtle-icon">⌘</span></div><div className="quick-grid">{quickActions.map(action => <button className="quick-card" key={action.key} onClick={() => onNavigate(action.key)}><span className={`quick-icon ${action.color}`}>{action.icon}</span><strong>{action.label}</strong><small>{action.help}</small><b>→</b></button>)}</div></section><section className="panel health-panel"><div className="panel-heading"><div><span className="eyebrow">INDICADORES</span><h2>Estado del negocio</h2></div><span className="status-chip">En línea</span></div><div className="health-list">{healthRows.map(({ label, value, icon }) => <div className="health-row" key={label}><span className="health-icon">{icon}</span><span>{label}</span><strong>{loading ? '…' : pretty(value)}</strong></div>)}</div><div className="health-footer"><span className="online-dot"/> Datos en tiempo real desde la API</div></section></div>
    <section className="panel attention-panel"><div className="panel-heading"><div><span className="eyebrow">ATENCIÓN</span><h2>Control de inventario</h2></div><button className="text-button" onClick={() => onNavigate('alertas')}>Ver alertas →</button></div><div className="attention-content"><div className="attention-symbol">!</div><div><strong>{pretty(data?.productos_bajo_stock)} productos con existencias bajas</strong><p>Consulta el inventario y programa la reposición necesaria.</p></div><button className="button secondary" onClick={() => onNavigate('alertas')}>Revisar productos</button></div></section>
  </div>
}

