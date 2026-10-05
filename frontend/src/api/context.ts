// Contexto do cliente de API: os hooks recebem o client por injeção (inversão de dependência).
import { createContext, useContext } from 'react'
import type { ApiClient } from './client'

export const ApiContext = createContext<ApiClient | null>(null)

export function useApi(): ApiClient {
  const client = useContext(ApiContext)
  if (!client) throw new Error('useApi precisa estar dentro de <ApiProvider>.')
  return client
}
