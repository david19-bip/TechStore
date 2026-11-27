import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Usuarios habilitado para el rol administrador. */
export const moduleKey = 'usuarios' as const
export default function UsuariosModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
