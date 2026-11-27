import type { Resource } from '../types'

const resource: Resource = { title: 'Bitácora de auditoría', endpoint: '/auditoria/', id: 'id_auditoria', columns: [{ key: 'fecha_evento', label: 'Fecha', format: 'date' }, { key: 'usuario_nombre', label: 'Usuario' }, { key: 'accion', label: 'Acción', format: 'status' }, { key: 'modulo', label: 'Módulo' }, { key: 'tabla_afectada', label: 'Tabla' }, { key: 'registro_id', label: 'Registro' }, { key: 'direccion_ip', label: 'IP' }] }

export default resource
