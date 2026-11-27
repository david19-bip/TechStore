import type { ComponentType } from 'react'
import type { PageKey, ResourcePageProps } from '../shared/types'
import Productos from './Productos'
import Categorias from './Categorias'
import Clientes from './Clientes'
import Proveedores from './Proveedores'
import Ventas from './Ventas'
import Compras from './Compras'
import Inventario from './Inventario'
import StockBajo from './StockBajo'
import Usuarios from './Usuarios'
import Auditoria from './Auditoria'

export const modulesAdministrador: Partial<Record<PageKey, ComponentType<ResourcePageProps>>> = {
  productos: Productos,
  categorias: Categorias,
  clientes: Clientes,
  proveedores: Proveedores,
  ventas: Ventas,
  compras: Compras,
  inventario: Inventario,
  alertas: StockBajo,
  usuarios: Usuarios,
  auditoria: Auditoria,
}
