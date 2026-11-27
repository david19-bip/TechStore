import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Productos habilitado para el rol bodeguero. */
export const moduleKey = 'productos' as const
export default function ProductosModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
