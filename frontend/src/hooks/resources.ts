// Hooks de dados por recurso. Cada um pede ao client injetado e devolve {data, error, loading, reload}.
import { useCallback } from 'react'
import { useApi } from '../api/context'
import type { AllocationException, AuditEvent, Policy, Signal, Sku, SkuPlan, Store, Summary } from '../api/types'
import { useAsync, type AsyncState } from './useAsync'

export function useSummary(): AsyncState<Summary> {
  const client = useApi()
  return useAsync(useCallback(() => client.getSummary(), [client]))
}

export function useExceptions(): AsyncState<AllocationException[]> {
  const client = useApi()
  return useAsync(useCallback(() => client.getExceptions(), [client]))
}

export function useSkus(): AsyncState<Sku[]> {
  const client = useApi()
  return useAsync(useCallback(() => client.getSkus(), [client]))
}

export function usePlan(sku: string | null): AsyncState<SkuPlan | null> {
  const client = useApi()
  return useAsync(useCallback(() => (sku ? client.getPlan(sku) : Promise.resolve(null)), [client, sku]))
}

export function useSignals(): AsyncState<Signal[]> {
  const client = useApi()
  return useAsync(useCallback(() => client.getSignals(), [client]))
}

export function usePolicies(): AsyncState<Policy[]> {
  const client = useApi()
  return useAsync(useCallback(() => client.getPolicies(), [client]))
}

export function useAuditLog(): AsyncState<AuditEvent[]> {
  const client = useApi()
  return useAsync(useCallback(() => client.getAuditLog(), [client]))
}

export function useStores(): AsyncState<Store[]> {
  const client = useApi()
  return useAsync(useCallback(() => client.getStores(), [client]))
}
