import ResourcePage from '../shared/ResourcePage'
import type { ResourcePageProps } from '../shared/types'

/** Módulo StockBajo habilitado para el rol bodeguero. */
export const moduleKey = 'alertas' as const
export default function StockBajoModule(props: ResourcePageProps) {
  return <ResourcePage {...props} />
}
