import type { Resource } from '../types'

const resource: Resource = { title: 'Productos', endpoint: '/productos/', id: 'id_producto', search: 'buscar', createRole: ['administrador'], deactivate: '/productos/{id}/desactivar', columns: [{ key: 'sku', label: 'SKU' }, { key: 'nombre', label: 'Producto' }, { key: 'marca', label: 'Marca' }, { key: 'categoria_nombre', label: 'Categoría' }, { key: 'precio_venta', label: 'Precio', format: 'money' }, { key: 'stock_actual', label: 'Existencias' }, { key: 'estado', label: 'Estado', format: 'status' }], fields: [
    { name: 'id_categoria', label: 'Categoría', type: 'select', required: true }, { name: 'sku', label: 'SKU', required: true }, { name: 'nombre', label: 'Nombre del producto', required: true }, { name: 'marca', label: 'Marca', required: true }, { name: 'descripcion', label: 'Descripción', wide: true }, { name: 'precio_compra', label: 'Precio de compra', type: 'number', required: true }, { name: 'precio_venta', label: 'Precio de venta', type: 'number', required: true }, { name: 'stock_actual', label: 'Stock inicial', type: 'number' }, { name: 'stock_minimo', label: 'Stock mínimo', type: 'number' },
  ] }

export default resource
