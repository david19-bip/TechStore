import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Auditoria habilitado para el rol administrador. */
export const moduleKey = 'auditoria' as const
export default function AuditoriaModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
