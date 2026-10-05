// ÚNICO ponto de fetch do frontend (api.md). Erros viram ApiError com a mensagem pt-BR do backend.
import type {
  AllocationException,
  AuditEvent,
  ChatMessage,
  CopilotAnswer,
  DecisionAction,
  ExceptionStatus,
  Health,
  Policy,
  Signal,
  SignalInterpretation,
  Sku,
  SkuPlan,
  Store,
  Summary,
  Transfer,
} from './types'

export class ApiError extends Error {
  readonly code: string
  readonly status: number

  constructor(code: string, message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

export type FetchLike = (input: string, init?: RequestInit) => Promise<Response>

export interface ApiClient {
  health(): Promise<Health>
  getSummary(): Promise<Summary>
  getSkus(): Promise<Sku[]>
  getStores(): Promise<Store[]>
  getPlan(sku: string): Promise<SkuPlan>
  getTransfers(): Promise<Transfer[]>
  getExceptions(status?: ExceptionStatus): Promise<AllocationException[]>
  decide(id: string, action: DecisionAction, reason?: string): Promise<AllocationException>
  getSignals(): Promise<Signal[]>
  interpretSignal(text: string, store?: string | null): Promise<SignalInterpretation>
  askCopilot(question: string, history: ChatMessage[], focusSku?: string | null): Promise<CopilotAnswer>
  getPolicies(): Promise<Policy[]>
  getAuditLog(limit?: number): Promise<AuditEvent[]>
}

const NETWORK_MESSAGE = 'Sem conexão com o servidor. Verifique a rede e tente de novo.'

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error
  return new ApiError('unexpected_error', 'Algo deu errado. Tente de novo.', 0)
}

export function createApiClient(fetchImpl: FetchLike = (input, init) => fetch(input, init), baseUrl = ''): ApiClient {
  async function request<T>(path: string, init?: RequestInit): Promise<T> {
    let response: Response
    try {
      response = await fetchImpl(`${baseUrl}${path}`, {
        ...init,
        headers: { 'Content-Type': 'application/json', Accept: 'application/json', ...init?.headers },
      })
    } catch {
      throw new ApiError('network_error', NETWORK_MESSAGE, 0)
    }
    const body: unknown = await response.json().catch(() => null)
    if (!response.ok) {
      const error = (body as { error?: { code?: string; message?: string } } | null)?.error
      throw new ApiError(
        error?.code ?? 'http_error',
        error?.message ?? `O servidor respondeu com erro (${response.status}).`,
        response.status,
      )
    }
    return body as T
  }

  const post = <T>(path: string, payload: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(payload) })

  return {
    health: () => request('/api/health'),
    getSummary: () => request('/api/summary'),
    getSkus: () => request('/api/skus'),
    getStores: () => request('/api/stores'),
    getPlan: (sku) => request(`/api/plan?sku=${encodeURIComponent(sku)}`),
    getTransfers: () => request('/api/transfers'),
    getExceptions: (status) => request(status ? `/api/exceptions?status=${status}` : '/api/exceptions'),
    decide: (id, action, reason) =>
      post(`/api/exceptions/${encodeURIComponent(id)}/decision`, reason ? { action, reason } : { action }),
    getSignals: () => request('/api/signals'),
    interpretSignal: (text, store) => post('/api/signals/interpret', store ? { text, store } : { text }),
    askCopilot: (question, history, focusSku) =>
      post('/api/copilot/ask', focusSku ? { question, history, focus_sku: focusSku } : { question, history }),
    getPolicies: () => request('/api/policies'),
    getAuditLog: (limit = 50) => request(`/api/audit-log?limit=${limit}`),
  }
}
