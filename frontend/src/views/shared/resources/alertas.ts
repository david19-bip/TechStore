import type { Resource } from '../types'

const resource: Resource = { title: 'Alertas de stock bajo', endpoint: '/inventario/alertas-stock', id: 'id_producto', columns: [{ key: 'sku', label: 'SKU' }, { key: 'nombre', label: 'Producto' }, { key: 'marca', label: 'Marca' }, { key: 'stock_actual', label: 'Existencias' }, { key: 'stock_minimo', label: 'Mínimo' }, { key: 'categoria_nombre', label: 'Categoría' }] }

export default resource
