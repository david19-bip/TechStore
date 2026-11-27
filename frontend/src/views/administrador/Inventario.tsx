import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Inventario habilitado para el rol administrador. */
export const moduleKey = 'inventario' as const
export default function InventarioModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
