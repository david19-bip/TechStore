import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { api, money } from './lib/api'
import type { PageKey, Resource, Row } from './views/shared/types'
import { resources } from './views/shared/resources'
import type { LoginResponse, User } from './lib/api'
import './App.css'
import VistaAdministrador from './views/administrador/Vista'
import VistaVendedor from './views/vendedor/Vista'
import VistaBodeguero from './views/bodeguero/Vista'
import { seccionesAdministrador } from './views/administrador/secciones'
import { seccionesVendedor } from './views/vendedor/secciones'
import { seccionesBodeguero } from './views/bodeguero/secciones'
import { modulesAdministrador } from './views/administrador/modules'
import { modulesVendedor } from './views/vendedor/modules'
import { modulesBodeguero } from './views/bodeguero/modules'
import ReportesAdministrador from './views/administrador/Reportes'


const rolesLabel: Record<string, string> = { administrador: 'Administrador', vendedor: 'Vendedor', bodeguero: 'Bodeguero' }
const navItems: { key: PageKey; label: string; group: string; icon: string; roles: string[] }[] = [
  { key: 'dashboard', label: 'Resumen', group: 'GENERAL', icon: '◫', roles: ['administrador', 'vendedor', 'bodeguero'] },
  { key: 'productos', label: 'Productos', group: 'CATÁLOGO', icon: '▦', roles: ['administrador', 'vendedor', 'bodeguero'] },
  { key: 'categorias', label: 'Categorías', group: 'CATÁLOGO', icon: '◈', roles: ['administrador'] },
  { key: 'clientes', label: 'Clientes', group: 'RELACIONES', icon: '♙', roles: ['administrador', 'vendedor'] },
  { key: 'proveedores', label: 'Proveedores', group: 'RELACIONES', icon: '▤', roles: ['administrador', 'bodeguero'] },
  { key: 'ventas', label: 'Ventas', group: 'OPERACIÓN', icon: '↗', roles: ['administrador', 'vendedor'] },
  { key: 'compras', label: 'Compras', group: 'OPERACIÓN', icon: '↙', roles: ['administrador', 'bodeguero'] },
  { key: 'inventario', label: 'Inventario', group: 'OPERACIÓN', icon: '◉', roles: ['administrador', 'bodeguero'] },
  { key: 'alertas', label: 'Stock bajo', group: 'OPERACIÓN', icon: '!', roles: ['administrador', 'vendedor', 'bodeguero'] },
  { key: 'reportes', label: 'Reportes', group: 'ANÁLISIS', icon: '▥', roles: ['administrador'] },
  { key: 'usuarios', label: 'Usuarios', group: 'ADMINISTRACIÓN', icon: '♧', roles: ['administrador'] },
  { key: 'auditoria', label: 'Auditoría', group: 'ADMINISTRACIÓN', icon: '◷', roles: ['administrador'] },
]

function Login({ onLogin }: { onLogin: (email: string, password: string) => Promise<void> }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { await onLogin(email.trim(), password) } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo iniciar sesión') } finally { setBusy(false) }
  }
  return <main className="login-shell"><div className="login-card"><div className="brand-mark large">T<span>.</span></div><div className="eyebrow">GESTIÓN INTELIGENTE</div><h1>Bienvenido a <span>TechStore</span></h1><p className="muted">Ingresa con tu cuenta para continuar.</p><form onSubmit={submit} className="login-form"><label>Correo electrónico<input type="email" autoComplete="username" placeholder="usuario@techstore.com" value={email} onChange={e => setEmail(e.target.value)} required /></label><label>Contraseña<input type="password" autoComplete="current-password" placeholder="Tu contraseña" value={password} onChange={e => setPassword(e.target.value)} required /></label>{error && <div className="alert error">{error}</div>}<button className="button primary full" disabled={busy}>{busy ? 'Validando…' : 'Iniciar sesión'} <span>→</span></button></form><div className="login-foot">API TechStore · Conexión segura por token</div></div><div className="login-decoration"><div className="deco-orb orb-one"/><div className="deco-orb orb-two"/><span className="deco-chip chip-a">LAPTOPS · AUDIO · GAMING</span><span className="deco-chip chip-b">TECNOLOGÍA LISTA PARA TI</span><div className="deco-panel"><div className="login-product-label"><span>TECHSTORE SELECTION</span><i>● EN STOCK</i></div><strong>Equipa tus ideas.<br/>Lleva tu mundo más lejos.</strong><small>Computadores, periféricos y tecnología para cada día.</small></div></div></main>
}

function App() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('techstore_token'))
  const [user, setUser] = useState<User | null>(() => { try { return JSON.parse(localStorage.getItem('techstore_user') || 'null') as User | null } catch { return null } })
  const [page, setPage] = useState<PageKey>('dashboard')
  const [rows, setRows] = useState<Row[]>([])
  const [dashboard, setDashboard] = useState<Row | null>(null)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [notice, setNotice] = useState<{ text: string; kind: 'success' | 'error' } | null>(null)
  const [dialog, setDialog] = useState<'create' | null>(null)
  const [editingRow, setEditingRow] = useState<Row | null>(null)
  const [reportType, setReportType] = useState('ventas')
  const [report, setReport] = useState<unknown>(null)
  const [categoryOptions, setCategoryOptions] = useState<{ value: number; label: string }[]>([])
  const [clientOptions, setClientOptions] = useState<{ value: number; label: string }[]>([])
  const [providerOptions, setProviderOptions] = useState<{ value: number; label: string }[]>([])
  const [productOptions, setProductOptions] = useState<Row[]>([])

  const allowedNav = useMemo(() => {
    const sections = user?.rol === 'administrador' ? seccionesAdministrador : user?.rol === 'vendedor' ? seccionesVendedor : seccionesBodeguero
    const allowedSections = new Set<string>(sections)
    return navItems.filter(item => allowedSections.has(item.key))
  }, [user])
  const resource = resources[page]
  const canCreate = Boolean(user && (resource?.createRole?.includes(user.rol) || (page === 'ventas' && ['administrador', 'vendedor'].includes(user.rol)) || (page === 'compras' && ['administrador', 'bodeguero'].includes(user.rol)) || (page === 'inventario' && ['administrador', 'bodeguero'].includes(user.rol))))

  const logout = useCallback(() => { localStorage.removeItem('techstore_token'); localStorage.removeItem('techstore_user'); setToken(null); setUser(null); setRows([]); setPage('dashboard') }, [])
  const loadPage = useCallback(async () => {
    if (!token) return
    setLoading(true)
    try {
      if (page === 'dashboard') {
        const data = await api<Row>('/reportes/dashboard', { token }); setDashboard(data)
      } else if (page === 'reportes') {
        const paths: Record<string, string> = { ventas: '/reportes/ventas', compras: '/reportes/compras', top: '/reportes/productos-mas-vendidos', finanzas: '/reportes/resumen-financiero' }
        setReport(await api(paths[reportType], { token }))
      } else if (resource) {
        const data = await api<unknown>(resource.endpoint, { token, query: resource.search ? { [resource.search]: search || undefined } : undefined })
        setRows(Array.isArray(data) ? data as Row[] : [])
      }
      setNotice(null)
    } catch (e) {
      if ('status' in (e as object) && ((e as { status?: number }).status === 401)) logout()
      else setNotice({ text: e instanceof Error ? e.message : 'No fue posible cargar la información', kind: 'error' })
    } finally { setLoading(false) }
  }, [page, resource, token, search, reportType, logout])

  useEffect(() => { void loadPage() }, [loadPage])
  useEffect(() => {
    if (!token) return
    void Promise.all([
      api<Row[]>('/categorias/', { token }).then(data => setCategoryOptions(data.map(x => ({ value: Number(x.id_categoria), label: String(x.nombre) })))) .catch(() => undefined),
      api<Row[]>('/clientes/', { token }).then(data => setClientOptions(data.map(x => ({ value: Number(x.id_cliente), label: `${String(x.nombre)} ${String(x.apellido)}` })))) .catch(() => undefined),
      api<Row[]>('/proveedores/', { token }).then(data => setProviderOptions(data.map(x => ({ value: Number(x.id_proveedor), label: String(x.razon_social) })))) .catch(() => undefined),
      api<Row[]>('/productos/', { token }).then(data => setProductOptions(data)) .catch(() => undefined),
    ])
  }, [token])

  async function login(email: string, password: string) {
    const result = await api<LoginResponse>('/auth/login', { method: 'POST', body: { email, password } })
    localStorage.setItem('techstore_token', result.access_token); localStorage.setItem('techstore_user', JSON.stringify(result.usuario)); setToken(result.access_token); setUser(result.usuario); setPage('dashboard')
  }
  async function createRecord(payload: Row) {
    if (!resource || !token) return
    await api(resource.endpoint, { method: 'POST', body: payload, token })
    setDialog(null); setEditingRow(null); await loadPage(); setNotice({ text: `${resource.title.slice(0, -1) || resource.title} creado correctamente.`, kind: 'success' })
  }
  async function updateRecord(payload: Row) {
    if (!resource || !token || !editingRow) return
    const id = editingRow[resource.id]
    const endpoint = `${resource.endpoint.replace(/\/$/, '')}/${String(id)}`
    await api(endpoint, { method: 'PUT', body: payload, token })
    setDialog(null); setEditingRow(null); await loadPage(); setNotice({ text: `${resource.title.slice(0, -1) || resource.title} actualizado correctamente.`, kind: 'success' })
  }
  async function deactivate(row: Row) {
    if (!resource?.deactivate || !token) return
    const id = row[resource.id]
    if (!window.confirm(`¿Desactivar este registro?`)) return
    try { await api(resource.deactivate.replace('{id}', String(id)), { method: 'PATCH', token }); await loadPage(); setNotice({ text: 'Registro desactivado correctamente.', kind: 'success' }) }
    catch (e) { setNotice({ text: e instanceof Error ? e.message : 'No se pudo desactivar', kind: 'error' }) }
  }
  async function processRowAction(row: Row, action: 'recibir' | 'anular') {
    if (!resource || !token) return
    const id = row[resource.id]
    const noun = resource.transaction === 'venta' ? 'venta' : 'compra'
    if (!window.confirm(action === 'recibir' ? '¿Marcar esta compra como recibida y actualizar existencias?' : `¿Anular esta ${noun}?`)) return
    try { await api(`/${resource.transaction === 'venta' ? 'ventas' : 'compras'}/${String(id)}/${action}`, { method: 'PATCH', token }); await loadPage(); setNotice({ text: action === 'recibir' ? 'Compra recibida y existencias actualizadas.' : `${noun[0].toUpperCase()}${noun.slice(1)} anulada correctamente.`, kind: 'success' }) }
    catch (e) { setNotice({ text: e instanceof Error ? e.message : 'No se pudo completar la operación', kind: 'error' }) }
  }
  function goTo(key: PageKey) { setPage(key); setSearch(''); setNotice(null); setDialog(null); if (key === 'reportes' && user?.rol === 'bodeguero') setReportType('compras'); else if (key === 'reportes' && user?.rol === 'vendedor') setReportType('ventas') }

  if (!token || !user) return <Login onLogin={login} />
  const groupedNav = [...new Set(allowedNav.map(item => item.group))]
  const modulesByRole = { administrador: modulesAdministrador, vendedor: modulesVendedor, bodeguero: modulesBodeguero }
  const ModuleView = modulesByRole[user.rol][page]
  return <div className="app-shell">
    <aside className="sidebar"><div className="brand"><div className="brand-mark">T<span>.</span></div><div><strong>techstore</strong><small>GESTIÓN COMERCIAL</small></div></div><div className="store-pill"><span className="online-dot"/> SISTEMA OPERATIVO</div><nav>{groupedNav.map(group => <div className="nav-group" key={group}><div className="nav-caption">{group}</div>{allowedNav.filter(item => item.group === group).map(item => <button className={`nav-link ${page === item.key ? 'active' : ''}`} key={item.key} onClick={() => goTo(item.key)}><span className="nav-icon">{item.icon}</span>{item.label}{item.key === 'inventario' && <span className="nav-arrow">›</span>}</button>)}</div>)}</nav><div className="sidebar-bottom"><div className="help-card"><div className="help-icon">?</div><strong>¿Necesitas ayuda?</strong><span>Consulta la documentación</span><a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">Abrir Swagger ↗</a></div><div className="profile"><div className="avatar">{user.nombre?.slice(0, 1)}{user.apellido?.slice(0, 1)}</div><div className="profile-info"><strong>{user.nombre} {user.apellido}</strong><small>{rolesLabel[user.rol] ?? user.rol}</small></div><button className="icon-button logout" title="Cerrar sesión" onClick={logout}>↪</button></div></div></aside>
    <main className="main-area"><header className="topbar"><div className="breadcrumb"><span>TechStore</span><b>/</b><strong>{navItems.find(x => x.key === page)?.label ?? 'Resumen'}</strong></div><div className="top-actions"><div className="api-health"><span className="online-dot"/> API conectada</div><div className="top-date">{new Date().toLocaleDateString('es-CO', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}</div><button className="icon-button bell" title="Notificaciones" onClick={() => goTo('inventario')}>♧</button></div></header>
      <section className="content-area">
        {notice && <div className={`alert ${notice.kind}`}><span>{notice.kind === 'success' ? '✓' : '!'}</span>{notice.text}<button onClick={() => setNotice(null)}>×</button></div>}
        {page === 'dashboard' ? user.rol === 'administrador' ? <VistaAdministrador data={dashboard} loading={loading} onNavigate={goTo} /> : user.rol === 'vendedor' ? <VistaVendedor data={dashboard} loading={loading} onNavigate={goTo} /> : <VistaBodeguero data={dashboard} loading={loading} onNavigate={goTo} /> : page === 'reportes' ? <ReportesAdministrador report={report} reportType={reportType} setReportType={setReportType} loading={loading} /> : resource && ModuleView ? <ModuleView resource={resource} rows={rows} loading={loading} search={search} setSearch={setSearch} onCreate={() => { setEditingRow(null); setDialog('create') }} onEdit={row => { setEditingRow(row); setDialog('create') }} canEdit={Boolean(resource.fields && resource.createRole?.includes(user.rol))} canCreate={canCreate} user={user} onDeactivate={deactivate} onRowAction={processRowAction} onRefresh={() => void loadPage()} /> : null}
      </section>
    </main>
    {dialog && resource && <CreateDialog resource={resource} token={token} categories={categoryOptions} clients={clientOptions} providers={providerOptions} products={productOptions} editRow={editingRow} onClose={() => setDialog(null)} onCreate={createRecord} onUpdate={updateRecord} onNotice={setNotice} onReload={loadPage} />}
  </div>
}



function CreateDialog({ resource, token, categories, clients, providers, products, editRow, onClose, onCreate, onUpdate, onNotice, onReload }: { resource: Resource; token: string; categories: { value: number; label: string }[]; clients: { value: number; label: string }[]; providers: { value: number; label: string }[]; products: Row[]; editRow: Row | null; onClose: () => void; onCreate: (payload: Row) => Promise<void>; onUpdate: (payload: Row) => Promise<void>; onNotice: (n: { text: string; kind: 'success' | 'error' } | null) => void; onReload: () => Promise<void> }) {
  if (resource.transaction) return <TransactionDialog kind={resource.transaction} token={token} clients={clients} providers={providers} products={products} onClose={onClose} onDone={async () => { await onReload(); onNotice({ text: resource.transaction === 'venta' ? 'Venta registrada correctamente.' : resource.transaction === 'compra' ? 'Compra registrada correctamente.' : 'Ajuste registrado correctamente.', kind: 'success' }) }} />
  const fields = (resource.fields ?? []).map(field => ({ ...field, ...(field.name === 'id_categoria' ? { options: categories } : {}), ...(field.name === 'password' && editRow ? { required: false } : {}) }))
  const initial = Object.fromEntries(fields.map(field => [field.name, editRow?.[field.name] !== undefined && editRow[field.name] !== null ? String(editRow[field.name]) : field.name === 'tipo_documento' ? 'CC' : field.name === 'estado' ? (resource.title === 'Categorías' ? 'activa' : 'activo') : field.type === 'number' ? '0' : '']))
  const [values, setValues] = useState<Record<string, string>>(initial)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try { const payload: Row = {}; for (const field of fields) { const value = values[field.name]; if (value !== undefined && value !== '') payload[field.name] = field.type === 'number' || field.type === 'select' && ['id_categoria'].includes(field.name) ? Number(value) : value } if (editRow) await onUpdate(payload); else await onCreate(payload) }
    catch (e) { const message = e instanceof Error ? e.message : 'No se pudo guardar'; setError(message); onNotice({ text: message, kind: 'error' }) }
    finally { setBusy(false) }
  }
  return <div className="modal-backdrop" onMouseDown={e => { if (e.target === e.currentTarget) onClose() }}><section className="modal-card"><div className="modal-head"><div><div className="eyebrow">{editRow ? 'ACTUALIZAR INFORMACIÓN' : 'NUEVO REGISTRO'}</div><h2>{editRow ? 'Editar' : 'Agregar'} {resource.title.toLowerCase().replace(/s$/, '')}</h2></div><button className="icon-button" onClick={onClose}>×</button></div><form onSubmit={submit}><div className="form-grid">{fields.map(field => <label className={field.wide ? 'wide-field' : ''} key={field.name}>{field.label}{field.type === 'select' ? <select value={values[field.name]} required={field.required} onChange={e => setValues({ ...values, [field.name]: e.target.value })}><option value="">Selecciona…</option>{field.options?.map(option => <option value={option.value} key={option.value}>{option.label}</option>)}</select> : field.wide ? <textarea rows={3} placeholder={field.placeholder ?? field.label} value={values[field.name]} required={field.required} onChange={e => setValues({ ...values, [field.name]: e.target.value })}/> : <input type={field.type ?? 'text'} min={field.type === 'number' ? 0 : undefined} step={field.type === 'number' ? 'any' : undefined} placeholder={field.placeholder ?? field.label} value={values[field.name]} required={field.required} onChange={e => setValues({ ...values, [field.name]: e.target.value })}/>}</label>)}</div>{error && <div className="alert error">{error}</div>}<div className="modal-actions"><button className="button secondary" type="button" onClick={onClose}>Cancelar</button><button className="button primary" disabled={busy}>{busy ? 'Guardando…' : editRow ? 'Guardar cambios' : 'Guardar registro'}</button></div></form></section></div>
}

function TransactionDialog({ kind, token, clients, providers, products, onClose, onDone }: { kind: 'venta' | 'compra' | 'ajuste'; token: string; clients: { value: number; label: string }[]; providers: { value: number; label: string }[]; products: Row[]; onClose: () => void; onDone: () => Promise<void> }) {
  const [party, setParty] = useState('')
  const [productId, setProductId] = useState('')
  const [qty, setQty] = useState('1')
  const [adjustmentType, setAdjustmentType] = useState('ajuste_positivo')
  const [reason, setReason] = useState('')
  const [method, setMethod] = useState('efectivo')
  const [items, setItems] = useState<{ product: Row; qty: number }[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const isAdjustment = kind === 'ajuste'
  const title = kind === 'venta' ? 'Registrar nueva venta' : kind === 'compra' ? 'Registrar nueva compra' : 'Ajuste de inventario'
  const options = kind === 'venta' ? clients : providers
  const product = products.find(item => String(item.id_producto) === productId)
  const unitPrice = Number(product?.[kind === 'compra' ? 'precio_compra' : 'precio_venta'] ?? 0)
  const subtotal = items.reduce((sum, item) => sum + Number(item.qty) * Number(item.product[kind === 'compra' ? 'precio_compra' : 'precio_venta'] ?? 0), 0)
  function addItem() { if (!product || Number(qty) < 1) return; const existing = items.findIndex(item => item.product.id_producto === product.id_producto); setItems(existing < 0 ? [...items, { product, qty: Number(qty) }] : items.map((item, index) => index === existing ? { ...item, qty: item.qty + Number(qty) } : item)); setProductId(''); setQty('1') }
  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError('')
    try {
      if (isAdjustment) {
        await api('/inventario/ajustes', { method: 'POST', token, body: { id_producto: Number(productId), tipo_movimiento: adjustmentType, cantidad: Number(qty), motivo: reason } })
      } else {
        if (!items.length) throw new Error('Agrega al menos un producto a la operación.')
        const body = kind === 'venta'
          ? { id_cliente: Number(party), metodo_pago: method, impuesto_porcentaje: 0, detalles: items.map(item => ({ id_producto: Number(item.product.id_producto), cantidad: item.qty, descuento: 0 })) }
          : { id_proveedor: Number(party), numero_factura: `FC-${Date.now()}`, impuesto_porcentaje: 0, estado: 'recibida', detalles: items.map(item => ({ id_producto: Number(item.product.id_producto), cantidad: item.qty, precio_unitario: Number(item.product.precio_compra ?? 0) })) }
        await api(kind === 'venta' ? '/ventas/' : '/compras/', { method: 'POST', token, body })
      }
      await onDone(); onClose()
    } catch (e) { setError(e instanceof Error ? e.message : 'No se pudo completar la operación') }
    finally { setBusy(false) }
  }
  return <div className="modal-backdrop" onMouseDown={e => { if (e.target === e.currentTarget) onClose() }}><section className="modal-card transaction-modal"><div className="modal-head"><div><div className="eyebrow">OPERACIÓN DE INVENTARIO</div><h2>{title}</h2></div><button className="icon-button" onClick={onClose}>×</button></div><form onSubmit={submit}><div className="form-grid">{!isAdjustment && <label className="wide-field">{kind === 'venta' ? 'Cliente' : 'Proveedor'}<select value={party} required onChange={e => setParty(e.target.value)}><option value="">Selecciona…</option>{options.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>}{isAdjustment && <label>Tipo de ajuste<select value={adjustmentType} onChange={e => setAdjustmentType(e.target.value)}><option value="ajuste_positivo">Entrada positiva</option><option value="ajuste_negativo">Salida negativa</option><option value="devolucion">Devolución</option></select></label>}{kind === 'venta' && <label>Método de pago<select value={method} onChange={e => setMethod(e.target.value)}><option value="efectivo">Efectivo</option><option value="tarjeta">Tarjeta</option><option value="transferencia">Transferencia</option><option value="pse">PSE</option></select></label>}<label className="wide-field">Producto<select value={productId} onChange={e => setProductId(e.target.value)} required={isAdjustment}><option value="">Selecciona un producto…</option>{products.filter(p => p.estado === 'activo').map(p => <option value={String(p.id_producto)} key={String(p.id_producto)}>{String(p.sku)} · {String(p.nombre)} (stock {String(p.stock_actual)})</option>)}</select></label><label>Cantidad<input type="number" min="1" step="1" value={qty} onChange={e => setQty(e.target.value)} required /></label>{isAdjustment && <label className="wide-field">Motivo<textarea rows={2} value={reason} onChange={e => setReason(e.target.value)} required minLength={3} placeholder="Describe el motivo del ajuste"/></label>}{!isAdjustment && <div className="add-line"><button type="button" className="button secondary" onClick={addItem} disabled={!product || Number(qty) < 1}>＋ Agregar producto</button>{product && <span>{money(unitPrice)} / unidad</span>}</div>}</div>{!isAdjustment && <div className="line-items">{items.length ? items.map((item, index) => <div className="line-item" key={`${item.product.id_producto}-${index}`}><div><strong>{String(item.product.nombre)}</strong><small>{item.qty} × {money(item.product[kind === 'compra' ? 'precio_compra' : 'precio_venta'])}</small></div><b>{money(item.qty * Number(item.product[kind === 'compra' ? 'precio_compra' : 'precio_venta']))}</b><button type="button" onClick={() => setItems(items.filter((_, i) => i !== index))}>×</button></div>) : <div className="line-empty">Agrega productos para calcular el total.</div>}<div className="transaction-total"><span>Total estimado · IVA 0%</span><strong>{money(subtotal)}</strong></div></div>}{error && <div className="alert error">{error}</div>}<div className="modal-actions"><button className="button secondary" type="button" onClick={onClose}>Cancelar</button><button className="button primary" disabled={busy}>{busy ? 'Procesando…' : isAdjustment ? 'Guardar ajuste' : kind === 'venta' ? 'Confirmar venta' : 'Registrar compra'}</button></div></form></section></div>
}


export default App
