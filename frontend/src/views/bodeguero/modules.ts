import type { ComponentType } from 'react'
import type { PageKey, ResourcePageProps } from '../shared/types'
import Productos from './Productos'
import Proveedores from './Proveedores'
import Compras from './Compras'
import Inventario from './Inventario'
import StockBajo from './StockBajo'

export const modulesBodeguero: Partial<Record<PageKey, ComponentType<ResourcePageProps>>> = {
  productos: Productos,
  proveedores: Proveedores,
  compras: Compras,
  inventario: Inventario,
  alertas: StockBajo,
}
