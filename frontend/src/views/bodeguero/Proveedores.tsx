import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Proveedores habilitado para el rol bodeguero. */
export const moduleKey = 'proveedores' as const
export default function ProveedoresModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
