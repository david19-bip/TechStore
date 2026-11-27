import type { Resource } from '../types'

const resource: Resource = { title: 'Categorías', endpoint: '/categorias/', id: 'id_categoria', createRole: ['administrador'], deactivate: '/categorias/{id}/desactivar', columns: [{ key: 'nombre', label: 'Nombre' }, { key: 'descripcion', label: 'Descripción' }, { key: 'estado', label: 'Estado', format: 'status' }, { key: 'creado_en', label: 'Creada', format: 'date' }], fields: [{ name: 'nombre', label: 'Nombre', required: true }, { name: 'descripcion', label: 'Descripción', wide: true }] }

export default resource
