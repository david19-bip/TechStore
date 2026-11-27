import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Clientes habilitado para el rol vendedor. */
export const moduleKey = 'clientes' as const
export default function ClientesModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
