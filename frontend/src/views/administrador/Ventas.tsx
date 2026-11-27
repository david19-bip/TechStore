import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Ventas habilitado para el rol administrador. */
export const moduleKey = 'ventas' as const
export default function VentasModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
