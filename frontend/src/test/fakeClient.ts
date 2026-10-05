// Client fake para os testes: nada de mock global de fetch (skill frontend-react).
import { vi } from 'vitest'
import type { ApiClient } from '../api/client'
import * as fx from './fixtures'

export type FakeClient = { [K in keyof ApiClient]: ReturnType<typeof vi.fn> & ApiClient[K] }

export function makeFakeClient(overrides: Partial<ApiClient> = {}): FakeClient {
  const base: ApiClient = {
    health: async () => ({ status: 'ok', llm: 'deterministic' }),
    getSummary: async () => fx.summary,
    getSkus: async () => fx.skus,
    getStores: async () => fx.stores,
    getPlan: async () => fx.plan,
    getTransfers: async () => [],
    getExceptions: async () => fx.exceptions,
    decide: async (id) => ({ ...fx.exceptions.find((e) => e.id === id)!, status: 'approved' }),
    getSignals: async () => fx.signals,
    interpretSignal: async () => fx.interpretation,
    askCopilot: async () => fx.copilot,
    getPolicies: async () => fx.policies,
    getAuditLog: async () => fx.audit,
  }
  const merged = { ...base, ...overrides }
  return Object.fromEntries(Object.entries(merged).map(([k, fn]) => [k, vi.fn(fn)])) as unknown as FakeClient
}
