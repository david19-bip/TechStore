import type { User } from '../../lib/api'

export type Row = Record<string, unknown>
export type PageKey = 'dashboard' | 'productos' | 'categorias' | 'clientes' | 'proveedores' | 'ventas' | 'compras' | 'inventario' | 'alertas' | 'reportes' | 'usuarios' | 'auditoria'
export type Field = { name: string; label: string; type?: string; required?: boolean; options?: { value: string | number; label: string }[]; wide?: boolean; placeholder?: string }
export type Resource = { title: string; endpoint: string; id: string; columns: { key: string; label: string; format?: 'money' | 'date' | 'status' }[]; fields?: Field[]; createRole?: string[]; deactivate?: string; transaction?: 'venta' | 'compra' | 'ajuste'; rowActions?: ('recibir' | 'anular')[]; search?: string }
export type ResourcePageProps = { resource: Resource; rows: Row[]; loading: boolean; search: string; setSearch: (s: string) => void; onCreate: () => void; onEdit: (r: Row) => void; canCreate: boolean; canEdit: boolean; user: User; onDeactivate: (r: Row) => void; onRowAction: (r: Row, action: 'recibir' | 'anular') => void; onRefresh: () => void }
