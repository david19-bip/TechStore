import type { Resource } from '../types'

const resource: Resource = { title: 'Ventas', endpoint: '/ventas/', id: 'id_venta', transaction: 'venta', rowActions: ['anular'], columns: [{ key: 'numero_factura', label: 'Factura' }, { key: 'cliente_nombre', label: 'Cliente' }, { key: 'fecha_venta', label: 'Fecha', format: 'date' }, { key: 'metodo_pago', label: 'Pago' }, { key: 'total', label: 'Total', format: 'money' }, { key: 'estado', label: 'Estado', format: 'status' }] }

export default resource
