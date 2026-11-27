import { useMemo } from 'react'
import { dateTime, money, pretty } from '../../lib/api'
import type { ResourcePageProps } from './types'

export default function ResourcePage({ resource, rows, loading, search, setSearch, onCreate, onEdit, canCreate, canEdit, user, onDeactivate, onRowAction, onRefresh }: ResourcePageProps) {
  const displayRows = useMemo(() => search.trim() ? rows.filter(row => Object.values(row).some(value => String(value ?? '').toLowerCase().includes(search.toLowerCase()))) : rows, [rows, search])
  const canDeactivate = Boolean(resource.deactivate && user.rol === 'administrador')
  const canReceive = Boolean(resource.rowActions?.includes('recibir') && ['administrador', 'bodeguero'].includes(user.rol))
  const canCancel = Boolean(resource.rowActions?.includes('anular') && user.rol === 'administrador')
  const hasActions = canEdit || canDeactivate || canReceive || canCancel
  return <div className="resource-page"><div className="page-heading"><div><div className="eyebrow">GESTIÓN TECHSTORE</div><h1>{resource.title}</h1><p className="muted">Consulta y administra los registros de {resource.title.toLowerCase()}.</p></div><div className="heading-actions"><button className="button secondary" onClick={onRefresh} title="Actualizar">↻ <span className="desktop-only">Actualizar</span></button>{canCreate && <button className="button primary" onClick={onCreate}><span>＋</span> {resource.transaction ? resource.transaction === 'venta' ? 'Nueva venta' : resource.transaction === 'compra' ? 'Nueva compra' : 'Registrar ajuste' : 'Nuevo registro'}</button>}</div></div>
    <section className="panel table-panel"><div className="table-toolbar"><div><strong>{displayRows.length}</strong> registros <span className="muted">· {resource.title}</span></div><label className="search-box"><span>⌕</span><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Buscar en la tabla…" /></label></div><div className="table-wrap"><table><thead><tr>{resource.columns.map(col => <th key={col.key}>{col.label}</th>)}{hasActions && <th className="actions-head">Acciones</th>}</tr></thead><tbody>{loading ? <tr><td colSpan={resource.columns.length + (hasActions ? 1 : 0)} className="empty-state"><span className="spinner"/> Cargando información…</td></tr> : displayRows.length ? displayRows.map((row, index) => <tr key={String(row[resource.id] ?? index)}>{resource.columns.map(col => <td key={col.key}>{resource.title === 'Productos' && col.key === 'nombre' ? <span className="product-name-cell"><span className="device-icon">{deviceGlyph(String(row.nombre ?? ''))}</span><span><strong>{pretty(row.nombre)}</strong><small>{pretty(row.sku)}</small></span></span> : renderCell(row[col.key], col.format)}</td>)}{hasActions && <td className="row-actions">{canEdit && <button className="row-action edit" onClick={() => onEdit(row)} title="Editar registro">Editar</button>}{canReceive && row.estado === 'pendiente' && <button className="row-action edit" onClick={() => onRowAction(row, 'recibir')}>Recibir</button>}{canCancel && row.estado !== 'anulada' && <button className="row-action" onClick={() => onRowAction(row, 'anular')}>Anular</button>}{canDeactivate && <button className="row-action" onClick={() => onDeactivate(row)} title="Desactivar registro">Desactivar</button>}</td>}</tr>) : <tr><td colSpan={resource.columns.length + (hasActions ? 1 : 0)} className="empty-state"><span className="empty-icon">⌕</span><strong>No hay registros para mostrar</strong><small>Prueba actualizar o cambia el término de búsqueda.</small></td></tr>}</tbody></table></div><div className="table-foot"><span>Mostrando {displayRows.length} de {rows.length} registros</span><span>Fuente: API TechStore</span></div></section></div>
}

function deviceGlyph(name: string) {
  const text = name.toLowerCase()
  if (text.includes('teclado')) return '⌨'
  if (text.includes('mouse') || text.includes('ratón')) return '⌖'
  if (text.includes('monitor') || text.includes('pantalla')) return '▣'
  if (text.includes('audífono') || text.includes('headphone') || text.includes('auricular')) return '◉'
  if (text.includes('celular') || text.includes('teléfono')) return '▯'
  if (text.includes('laptop') || text.includes('portátil')) return '▱'
  return '✦'
}
function renderCell(value: unknown, format?: string) {
  if (format === 'money') return <strong className="money-cell">{money(value)}</strong>
  if (format === 'date') return <span className="date-cell">{dateTime(value)}</span>
  if (format === 'status') return <span className={`status-tag ${String(value).toLowerCase()}`}>{pretty(value)}</span>
  return <span>{pretty(value)}</span>
}
