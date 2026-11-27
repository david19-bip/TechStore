import type { PageKey, Resource } from './types'
import productos from './resources/productos'
import categorias from './resources/categorias'
import clientes from './resources/clientes'
import proveedores from './resources/proveedores'
import ventas from './resources/ventas'
import compras from './resources/compras'
import inventario from './resources/inventario'
import alertas from './resources/alertas'
import usuarios from './resources/usuarios'
import auditoria from './resources/auditoria'

export const resources: Partial<Record<PageKey, Resource>> = {
  productos: productos,
  categorias: categorias,
  clientes: clientes,
  proveedores: proveedores,
  ventas: ventas,
  compras: compras,
  inventario: inventario,
  alertas: alertas,
  usuarios: usuarios,
  auditoria: auditoria
}
