import ReportsPage from '../shared/ReportsPage'

type Props = { report: unknown; reportType: string; setReportType: (value: string) => void; loading: boolean }

/** Módulo de reportes exclusivo del administrador. */
export default function ReportesAdministrador(props: Props) {
  return <ReportsPage {...props} role="administrador" />
}
