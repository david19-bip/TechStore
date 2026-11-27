import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo Categorias habilitado para el rol administrador. */
export const moduleKey = 'categorias' as const
export default function CategoriasModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
