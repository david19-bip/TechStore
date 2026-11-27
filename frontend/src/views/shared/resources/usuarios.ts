import type { Resource } from '../types'

const resource: Resource = { title: 'Usuarios', endpoint: '/usuarios/', id: 'id_usuario', createRole: ['administrador'], deactivate: '/usuarios/{id}/desactivar', columns: [{ key: 'nombre', label: 'Nombre' }, { key: 'apellido', label: 'Apellido' }, { key: 'email', label: 'Correo' }, { key: 'rol', label: 'Rol', format: 'status' }, { key: 'estado', label: 'Estado', format: 'status' }], fields: [{ name: 'nombre', label: 'Nombre', required: true }, { name: 'apellido', label: 'Apellido', required: true }, { name: 'email', label: 'Correo electrónico', type: 'email', required: true }, { name: 'password', label: 'Contraseña inicial', type: 'password', required: true }, { name: 'rol', label: 'Rol', type: 'select', required: true, options: [{ value: 'administrador', label: 'Administrador' }, { value: 'vendedor', label: 'Vendedor' }, { value: 'bodeguero', label: 'Bodeguero' }] }] }

export default resource
