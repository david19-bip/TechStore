import type { Resource } from '../types'

const resource: Resource = { title: 'Compras', endpoint: '/compras/', id: 'id_compra', transaction: 'compra', rowActions: ['recibir', 'anular'], columns: [{ key: 'numero_factura', label: 'Factura' }, { key: 'proveedor_nombre', label: 'Proveedor' }, { key: 'fecha_compra', label: 'Fecha', format: 'date' }, { key: 'total', label: 'Total', format: 'money' }, { key: 'estado', label: 'Estado', format: 'status' }] }

export default resource
