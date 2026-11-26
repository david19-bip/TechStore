import type { User } from '../../lib/api'
import DashboardView from '../shared/DashboardView'

type Props = { data: Record<string, unknown> | null; loading: boolean; onNavigate: (key: 'dashboard' | 'productos' | 'categorias' | 'clientes' | 'proveedores' | 'ventas' | 'compras' | 'inventario' | 'alertas' | 'reportes' | 'usuarios' | 'auditoria') => void }

/** Vista de inicio específica para el rol vendedor; las demás secciones permitidas se comparten. */
export default function VistaVendedor({ data, loading, onNavigate }: Props) {
  const role: User['rol'] = 'vendedor'
  return <DashboardView data={data} loading={loading} onNavigate={onNavigate} role={role} />
}
