import type { Resource } from '../types'

const resource: Resource = { title: 'Movimientos de inventario', endpoint: '/inventario/movimientos', id: 'id_movimiento', transaction: 'ajuste', columns: [{ key: 'fecha_movimiento', label: 'Fecha', format: 'date' }, { key: 'producto_sku', label: 'SKU' }, { key: 'producto_nombre', label: 'Producto' }, { key: 'tipo_movimiento', label: 'Movimiento' }, { key: 'cantidad', label: 'Cantidad' }, { key: 'stock_anterior', label: 'Anterior' }, { key: 'stock_nuevo', label: 'Nuevo' }, { key: 'motivo', label: 'Motivo' }] }

export default resource
