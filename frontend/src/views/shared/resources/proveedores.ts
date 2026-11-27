import type { Resource } from '../types'

const resource: Resource = { title: 'Proveedores', endpoint: '/proveedores/', id: 'id_proveedor', search: 'buscar', createRole: ['administrador'], deactivate: '/proveedores/{id}/desactivar', columns: [{ key: 'nit', label: 'NIT' }, { key: 'razon_social', label: 'Razón social' }, { key: 'nombre_contacto', label: 'Contacto' }, { key: 'telefono', label: 'Teléfono' }, { key: 'ciudad', label: 'Ciudad' }, { key: 'estado', label: 'Estado', format: 'status' }], fields: [{ name: 'nit', label: 'NIT', required: true }, { name: 'razon_social', label: 'Razón social', required: true }, { name: 'nombre_contacto', label: 'Nombre del contacto' }, { name: 'telefono', label: 'Teléfono' }, { name: 'email', label: 'Correo electrónico', type: 'email' }, { name: 'ciudad', label: 'Ciudad' }, { name: 'direccion', label: 'Dirección', wide: true }] }

export default resource
