import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Compras habilitado para el rol administrador. */
export const moduleKey = 'compras' as const
export default function ComprasModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
