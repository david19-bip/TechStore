const API_ROOT = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const API_PREFIX = `${API_ROOT}/api/v1`

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export type RequestOptions = {
  method?: string
  body?: unknown
  token?: string | null
  query?: Record<string, string | number | boolean | undefined | null>
}

export async function api<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const url = new URL(`${API_PREFIX}${path.startsWith('/') ? path : `/${path}`}`)
  for (const [key, value] of Object.entries(options.query ?? {})) {
    if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, String(value))
  }
  const headers: Record<string, string> = { Accept: 'application/json' }
  if (options.body !== undefined) headers['Content-Type'] = 'application/json'
  if (options.token) headers.Authorization = `Bearer ${options.token}`
  const response = await fetch(url, {
    method: options.method ?? 'GET',
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body),
  })
  if (response.status === 204) return undefined as T
  const text = await response.text()
  let payload: unknown = null
  try { payload = text ? JSON.parse(text) : null } catch { payload = text }
  if (!response.ok) {
    const detail = typeof payload === 'object' && payload !== null && 'detail' in payload
      ? String((payload as { detail: unknown }).detail)
      : typeof payload === 'string' ? payload : `Error HTTP ${response.status}`
    throw new ApiError(detail, response.status)
  }
  return payload as T
}

export type User = {
  id_usuario: number
  nombre: string
  apellido: string
  email: string
  rol: 'administrador' | 'vendedor' | 'bodeguero'
  estado: string
}

export type LoginResponse = { access_token: string; token_type: string; usuario: User }
export const money = (value: unknown) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(Number(value ?? 0))
export const dateTime = (value: unknown) => value ? new Date(String(value)).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' }) : '—'
export const pretty = (value: unknown) => {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'boolean') return value ? 'Sí' : 'No'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}
