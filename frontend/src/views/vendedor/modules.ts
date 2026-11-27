import type { ComponentType } from 'react'
import type { PageKey, ResourcePageProps } from '../shared/types'
import Productos from './Productos'
import Clientes from './Clientes'
import Ventas from './Ventas'
import StockBajo from './StockBajo'

export const modulesVendedor: Partial<Record<PageKey, ComponentType<ResourcePageProps>>> = {
  productos: Productos,
  clientes: Clientes,
  ventas: Ventas,
  alertas: StockBajo,
}
